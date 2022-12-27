addLoadEvent(() => {
    const mail_regex = new RegExp("^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$");
    const phone_regex = new RegExp("^[0-9]{9,10}$");
    const pass_regex = new RegExp("^[a-zA-Z0-9.!@#$%&*]{8,64}$");

    let fields = document.getElementsByClassName("field");
    let labels = document.getElementsByName("label");
    let mail_field = document.getElementById("email-field");
    let password_field = document.getElementById("password-field");

    if (mail_field.value !== "") {
        if ((mail_regex.test(mail_field.value) || phone_regex.test(mail_field.value)) && !mail_field.className.includes("filled")) {
            mail_field.className += " filled";
        }

        if (!mail_field.className.includes("incorrect")) {
            mail_field.className += " incorrect";
        }
    }

    for (let label of labels) {
        label.addEventListener("click", (e)=> {
            e.preventDefault();
        });
    }

    for (let field of fields) {
        field.addEventListener("focus", () => {
            field.className = field.className.replaceAll(" incorrect", "")
            .replaceAll(" filled", "");
        })
    }

    mail_field.addEventListener("focusout", ()=> {
        if ((mail_regex.test(mail_field.value) || phone_regex.test(mail_field.value)) && !mail_field.className.includes("filled")) {
            mail_field.className += " filled";
            return;
        }

        if (!mail_field.className.includes("incorrect")) {
            mail_field.className += " incorrect";
        }
    });

    password_field.addEventListener("focusout", ()=> {
        if (pass_regex.test(password_field.value) && !password_field.className.includes("filled")) {
            password_field.className += " filled";
            return;
        }

        if (!password_field.className.includes("incorrect")) {
            password_field.className += " incorrect";
        }
    });
});

async function log_in() {
    let correct = document.getElementById("email-field").className.includes("filled") &&
    document.getElementById("password-field").className.includes("filled");

    if (!correct) return;

    let email = document.getElementById("email-field").value;
    let password = document.getElementById("password-field").value;

    /* Verify if email is correct */
    let data = JSON.parse(await (await fetch("/login", {
        method: "POST",
        body: JSON.stringify({
            email_check: true,
            email: email
        })
    })).text());

    if (!data['success']) {
        let incorrect_email = document.getElementById("incorrect-email");
        incorrect_email.innerHTML = data['message'];
        setTimeout(async () => {
            await sleep(5000);
            incorrect_email.innerHTML = "";
        })
        return;
    }

    /* Send actual data */
    data = JSON.parse(await (await fetch("/resource/encryption-data", {method: "GET"})).text());

    let enc = Cipher.static_encrypt(JSON.stringify({
        email: email,
        password: password
    }), data['key'], data['separator'], data['max_message_length']);

    data = JSON.parse(await (await fetch("/login", {
        method: "POST",
        body: enc
    })).text())

    if (!data['success']) {
        let incorrect_password = document.getElementById("incorrect-password");
        incorrect_password.innerHTML = "INCORRECT PASSWORD!";
        setTimeout(async () => {
            await sleep(5000);
            incorrect_password.innerHTML = "";
        })
        return;
    }

    window.location.replace("/app");
}