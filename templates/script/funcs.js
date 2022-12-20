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