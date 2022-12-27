addLoadEvent(() => {
    let header = document.getElementById("main-box").querySelector(".header")[0];
    let sub = document.getElementById("main-box").querySelector(".sub")[0];

    header.innerHTML = header.innerText;
    sub.innerHTML = sub.innerText;
})

async function request_email(email) {
    let response = JSON.parse(await (await fetch(`/request-verification`, {
        method: "POST",
        body: JSON.stringify({
            email: email
        })
    })).text())

    let response_box = document.getElementById("response-box");
    let main_box = document.getElementById("main-box");

    let header = document.getElementById("response-box").querySelector(".header")[0];
    let sub = document.getElementById("response-box").querySelector(".sub")[0];

    header.innerHTML = response['header'];
    sub.innerHTML = response['sub'];

    if (Object.keys(response).includes('buttons')) {
        for (let button of response.buttons) {
            let btn = document.createElement("div");
            btn.className = "button";
            btn.innerHTML = button.content;
            btn.addEventListener("click", () => {
                eval(button.onclick);
            });

            if (Object.keys(button).includes("style")) {
                btn.setAttribute("style", button.style);
            }

            response_box.appendChild(btn);
        }
    }

    main_box.style.display = "none";
    response_box.style.display = "";
}

function login_redirect(email) {
    window.location.replace(`/login?login=${btoa(email)}`);
}