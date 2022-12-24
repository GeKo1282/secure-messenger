addLoadEvent(() => {
    const mail_regex = new RegExp("^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$");
    const phone_regex = new RegExp("^[0-9]{9,10}$");

    let fields = document.getElementsByClassName("field");
    let labels = document.getElementsByName("label");
    let mail_field = document.getElementById("email-field");

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
});