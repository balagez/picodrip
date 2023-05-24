'use strict';

/* global React, ReactDOM */

const serverZoneOffset = -4; // New York

const pumpNames = {
	1: 'Flowers',
	2: 'Ficus',
	3: 'Basil',
	4: 'Succu',
};

const e = (name, props, children) => React.createElement(name, props, children);
const div = (props, ...children) => e('div', props, children);
const span = (props, ...children) => e('span', props, children);
const label = (props, ...children) => e('label', props, children);
const img = (props) => e('img', props);
const text = (props) => e('input', {type: 'text', ...props});
const checkbox = (props) => e('input', {type: 'checkbox', ...props});
const svg = (props, ...children) => e('svg', { xmlns: 'http://www.w3.org/2000/svg', ...props }, ...children);
const path = (props) => e('path', props);

const iconSchedule = ({ key }) => svg({ key, width: 12, heigh: 12, viewBox: '0 0 18 18' },
	path({ fillRule: 'evenodd', d: 'M9 17A8 8 0 1 1 9 1a8 8 0 0 1 0 16zm0-1A7 7 0 1 0 9 2a7 7 0 0 0 0 14zM8.5 4c.28 0 .5.22.5.5v4.72l3.79 2.42a.5.5 0 0 1-.54.84L8.3 9.96A.5.5 0 0 1 8 9.5v-5c0-.28.22-.5.5-.5z' })
);

const iconManual = ({ key }) => svg({ key, width: 12, heigh: 12, viewBox: '0 0 18 18' },
	path({ fillRule: 'evenodd', d: 'M9 1c1.4 0 2.27.5 3.02 1.57a6.04 6.04 0 0 1 .57 5.3 8.82 8.82 0 0 1-.96 1.88l-.06.09-.21.33-.02.05.03.02.16.08.04.03c.11.06.7.31 1.84.77l.02.01c1.85.75 1.93.78 2.06.88a3 3 0 0 1 1.24 2.01 17.97 17.97 0 0 1 .23 1.99l.04.44a.5.5 0 0 1-.5.54L1.5 17a.5.5 0 0 1-.5-.54 50.27 50.27 0 0 1 .28-2.48 3 3 0 0 1 1.23-1.97c.13-.1.7-.34 2.01-.88l.06-.02 1.94-.8c.13-.05.16-.06.16-.1a37.57 37.57 0 0 1-.52-.78 9.75 9.75 0 0 1-.76-1.55c-.66-1.7-.4-3.9.56-5.3C6.75 1.44 7.53 1 9 1zm0 1c-1.12 0-1.6.28-2.2 1.14a5.05 5.05 0 0 0-.46 4.37c.39.99.56 1.28 1.2 2.2l.07.12c.23.66-.08 1.14-.7 1.4l-1.95.8-.06.03c-1 .4-1.78.74-1.81.76a2.01 2.01 0 0 0-.83 1.34A16.17 16.17 0 0 0 2.05 16l13.9-.01a50.3 50.3 0 0 0-.2-1.8 2.09 2.09 0 0 0-.84-1.37c-.02-.02-.57-.24-1.85-.76l-.03-.01a23.58 23.58 0 0 1-2.23-.98c-.48-.24-.6-.64-.35-1.31l.28-.46.06-.09a8 8 0 0 0 .87-1.7 5.05 5.05 0 0 0-.46-4.37A2.35 2.35 0 0 0 9 2z' })
);

const group = (array, fn) => array.reduce((acc, curr) => {
	const group = fn(curr);
	if (!acc[group]) {
		acc[group] = [];
	}
	acc[group].push(curr);
	return acc;
}, {});

const oneHour = 60 * 60 * 1000;
const oneDay = 24 * oneHour;

const serverTime = localTime => {
	if (!localTime) {
		localTime = new Date();
	}
	return new Date(localTime.getTime() + localTime.getTimezoneOffset() * 60000 + serverZoneOffset * oneHour);
};

const mapValues = (obj, fn) => Object.fromEntries(Object.entries(obj).map(([k, v]) => [k, fn(v)]));

const daysAgo = date => {
	const now = serverTime();
	const then = new Date(date.getTime());
	then.setHours(0, 0, 0, 0);
	now.setHours(0, 0, 0, 0);
	return (+now - +then) / oneDay;
};

const weekdayOf = date => date.toLocaleDateString('en-US', { weekday: 'short' });

const relativeDate = daysAgo => {
	if (daysAgo == 0) return 'Today';
	if (daysAgo == 1) return 'Yesterday';
	if (daysAgo > 1 && daysAgo < 7) return `${daysAgo} days ago`;
	const date = new Date(serverTime() - oneDay * daysAgo);
	const m = date.toLocaleString('en-US', { month: 'short' });
	const d = date.getDate();
	const wd = weekdayOf(date);
	return `${m} ${d}, ${wd}`;
};

const yPosOf = e => {
	const rect = e.getBoundingClientRect();
	const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
	return rect.top + scrollTop;
};

const send = async cmd => {
	console.log(`sending command: ${cmd}`);
	const res = await fetch('/api/command', {
		method: 'POST',
		headers: {'Content-Type': 'text/plain'},
		body: cmd
	});
	if (res.status != 200) {
		let err = await res.text();
		try { err = JSON.parse(err).error; } catch (e) {}
		throw new Error(err);
	}
	return await res.json();
};

const getPumpLogs = async () => {
	const res = await fetch('/pumps.log');
	const raw = await res.text();
	if (res.status != 200) {
		throw new Error(raw);
	}
	let parsed = [];
	raw.split('\n').forEach(line => {
		line = line.trim();
		if (line) {
			let [ ts, i, v, caller, ...rest ] = line.trim().split(' ');
			const date = serverTime(new Date(Number(ts) * 1000));
			parsed.push({
				pump: Number(i),
				value: Number(v),
				daysAgo: daysAgo(date),
				date,
				caller,
			});
		}
	});
	parsed = group(parsed, ({ pump }) => pump);
	return mapValues(parsed, logs => {
		const aggregated = logs.reduce((acc, curr) => {
			const { value, date } = curr;
			if (value === 1) {
				return [curr, ...acc];
			} else if (value === 0 && acc.length) {
				const [head, ...tail] = acc;
				if (typeof head.duration === 'undefined') {
					const duration = (date - head.date) / 1000;
					return [{...head, duration}, ...tail];
				}
			}
			return acc;
		}, []);
		return group(aggregated, ({ daysAgo }) => daysAgo);
	});
}

const Section = ({ key, className, title = null }, ...children) => [
	title && e('h2', { key: `${key}-title` }, title),
	e('section', { key: `${key}-section`, className }, children)
];

const Header = () => Section({ key: 'header', className: 'header' }, 'PicoDrip');

const Label = ({ key }, ...children) => span({ key: `${key}-label`, className: 'label' }, children);

const Value = ({ key }, ...children) => span({ key: `${key}-value`, className: 'value' }, children);

const Info = ({ time, temp }) => {
	const date = new Date(time * 1000);
	const options = { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
	const formattedDate = date.toLocaleString('en-US', options).replace(/(\d+)\/(\d+)\/(\d+)/, '$3-$1-$2').replace(',', '');
	return Section({ key: 'info', className: 'info' },
		Label({ key: 'info-time' }, 'Time'),
		Value({ key: 'info-time' }, `${formattedDate} ET`),
		Label({ key: 'info-temp' }, 'Temperature'),
		Value({ key: 'info-temp' }, `${temp.toFixed(1)}°C`)
	);
}

const Pump = ({ id, name, schedule, on, onActivate }) => {
	const key = `pump-${id}`;
	return div({ key: `${key}-d` },
		span({ key: `${key}-l`, className: 'label' }, name),
		label({ key: `${key}-sw-l`, className: 'switch' },
			checkbox({ key: `${key}-sw-cb`, checked: on, onChange: e => onActivate(id, e.target.checked) }),
			span({ key: `${key}-sw-sl`, className: 'slider' })
		)
	);
};

const HistoryTable = history => {
	const allDays = [...new Set(Object.values(history).map(Object.keys).flat())].sort();

	const pumpIndices = Object.keys(pumpNames);

	const header = Object.values(pumpNames).map(name =>
		div({ key: `h-pl-${name}`, className: 'pump' }, name)
	);

	const cellsFor = daysAgo => pumpIndices.map(pump => {
		const cellKey = `h-c-${pump}-${daysAgo}`;
		const entries = (history[pump] || {})[daysAgo];
		const children = entries
			? entries.map(({ date, duration, caller }) => {
				const key = `${cellKey}-${date}`;
				return div({ key, className: `time ${caller}` },
					caller === 'scheduler'
						? iconSchedule({ key: `${key}-icon` })
						: iconManual({ key: `${key}-icon` }),
					span({ key: `${key}-h`, className: 'h' }, date.getHours().toString().padStart(2, '0')),
					span({ key: `${key}-m`, className: 'm' }, ':' + date.getMinutes().toString().padStart(2, '0')),
					// span({ key: `${key}-s`, className: 's' }, ':' + date.getSeconds().toString().padStart(2, '0')),
					duration ? ` ${duration}s` : ' ON',
				)
			})
			: [];
		return div({ key: cellKey, className: 'log' }, ...children);
	});

	const rows = allDays.map(daysAgo => [
		div({ key: `h-d-${daysAgo}`, className: `day day-${daysAgo}` }, relativeDate(daysAgo)),
		...cellsFor(daysAgo)
	]);

	return [
		...header,
		...rows
	];
};

const App = initialState => {
	const [state, setState] = React.useState(initialState);
	const [history, setHistory] = React.useState(null);
	const [error, setError] = React.useState(null);
	const scheduleRef = React.useRef(null);

	const clearErrors = () => setError(null);
	const handleError = top => e => setError({ top, message: e.message} );

	const refreshState = async () => {
		setState(await send('state'));
		clearErrors();
	};

	const onActivate = async (id, value) => {
		const duration = 5000;
		return send(`pump ${id} ${value ? `on ${duration}` : 'off'}`)
			.then(state => {
				setState(state);
				clearErrors();
				window.setTimeout(refreshState, duration + 200);
			})
			.catch(handleError(290));
	};

	const onScheduleChange = e => {
		clearErrors();
		const ref = scheduleRef.current;
		const newSchedule = ref.value;
		const y = yPosOf(ref) + parseInt(ref.style.height) + 4;
		if (state.schedule.join('\n') !== newSchedule) {
			send(`schedule\n${newSchedule}`)
				.then(state => {
					setState(state);
				})
				.catch(handleError(y));
			}
	};

	const createPump = (id, name) => Pump({
		id,
		name,
		schedule: state[`schedule${id}`],
		on: state[`pump${id}`],
		onActivate
	});
	
	const autoResize = textarea => {
		const h = textarea.scrollHeight; // this is needed to avoid some race condition
		textarea.style.height = 'auto';
		textarea.style.height = `${textarea.scrollHeight}px`;
	};
	
	React.useEffect(() => autoResize(scheduleRef.current), []);
	React.useEffect(() => { getPumpLogs().then(setHistory).catch(handleError) }, []);

	return [
		error ? div({ key: 'error-popup', className: 'error-popup', style: { top: `${error.top}px` } }, error.message) : undefined,
		Header(),
		Info({ time: state.time, temp: state.temp }),
		Section({ key: 'pumps', className: 'pumps', title: 'Pumps' },
			createPump('1', pumpNames[1]),
			createPump('2', pumpNames[2]),
			createPump('3', pumpNames[3]),
			createPump('4', pumpNames[4])
		),
		Section({ key: 'schedule', className: 'schedule', title: 'Schedule' },
			e('textarea', {
				ref: scheduleRef,
				key: 'schedule',
				onInput: e => autoResize(e.target),
				onBlur: onScheduleChange,
				defaultValue: state.schedule.join('\n')
			})
		),
		Section({ key: 'history', className: 'history', title: 'History' }, history ? HistoryTable(history) : null)
	];
};

window.addEventListener('DOMContentLoaded', () => {
	const c = document.getElementById('react-root');
	ReactDOM.createRoot(c).render(e(App, JSON.parse(c.dataset.state)));
});
