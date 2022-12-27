const sleep = ms => new Promise(r => setTimeout(r, ms));

function addLoadEvent(func) {
    let oldonload = window.onload;
	if (typeof window.onload != 'function') {
		window.onload = func;
	} else {
		window.onload = function() {
			if (oldonload) {
			    try {
			        oldonload();
                } catch (e) {console.log("%c" + e.stack, "color: red;");}

			}

			try {
			    func();
			} catch (e) {console.log("%c" + e.stack, "color: red;");}

		}
	}
}

function range(start, end, step=1) {
	let out = [];
	let i = start;
	while (i + step <= end + 1) {
		out.push(i);
		i += step;
	}

	if (out[out.length-1] !== end) {
		out.push(end);
	}

	if (out[0] !== 0) {
		out = [0].concat(out)
	}
	return out;
}