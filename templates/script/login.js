addLoadEvent(() => {
    let fields = document.getElementsByClassName("field");
    let pass_field = document.getElementById("password").children[0].children[0];
    let eye = document.getElementById("eye");
    let eye_stroke = document.getElementById("eye-stroke");

    function refresh_eye() {
        if (pass_field.innerHTML !== '' && (pass_field.dataset.shown === 'false' || pass_field.dataset.shown === 'undefined')) {
            eye.style.display = "block";
            eye_stroke.style.display = "none";
        } else if (pass_field.innerHTML === '') {
            eye.style.display = 'none';
            eye_stroke.style.display = 'none';
        } else {
            eye.style.display = 'none';
            eye_stroke.style.display = 'block';
        }
    }

    for (let field of fields) {
        let span = field.children[0].children[0];
        field.addEventListener("click",  () => {
            span.contentEditable = true;
            span.focus();
        });

        span.innerText = span.dataset.placeholder;
        span.style.color = "#999";
        span.addEventListener("focus", () => {
            span.contentEditable = true;
            if (span.innerText === span.dataset.placeholder) {
                span.innerText = "";
                span.style.color = "#444";
            }
        });

        span.addEventListener("focusout", () => {
            span.contentEditable = false;
            if (span.innerHTML.toString().replaceAll(' ', '').replaceAll("&nbsp;", '') === "") {
                span.innerText = span.dataset.placeholder;
                span.style.color = "#999";
            }
        });
    }

    pass_field.addEventListener("focus", () => {
        if (pass_field.style['font-family'] === '' && pass_field.innerHTML.toString().replaceAll(' ', '').replaceAll("&nbsp;", '') === '') {
            pass_field.style['font-family'] = 'password';
        }
    });

    pass_field.addEventListener("focusout", () => {
        if (pass_field.innerText === pass_field.dataset.placeholder) {
            pass_field.style['font-family'] = '';
        }
    });

    eye.onclick = () => {
        setTimeout(async () => {
            await sleep(100);
            pass_field.dataset.shown = 'true';
            pass_field.style['font-family'] = '';
            refresh_eye();
        });
    }

    eye_stroke.onclick = () => {
        setTimeout(async () => {
            await sleep(100);
            pass_field.dataset.shown = 'false';
            pass_field.style['font-family'] = 'password';
            refresh_eye();
        });
    }

    pass_field.addEventListener("input", () => {
        refresh_eye();
    })
});