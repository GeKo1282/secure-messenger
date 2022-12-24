addLoadEvent(() => {
    const mail_regex = new RegExp("^[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$");
    const phone_regex = new RegExp("^[0-9]{9,10}$");
    const pass_regex = new RegExp("^[a-zA-Z0-9.!@#$%&*]{8,64}$");

    let fields = document.getElementsByClassName("field");
    let labels = document.getElementsByName("label");
    let mail_field = document.getElementById("email-field");
    let password_field = document.getElementById("password-field");
    let nick_field = document.getElementById("nick-field");
    let repeat_field = document.getElementById("repeat-password-field");

    let min_char_check = document.getElementById("8-char-check");
    let max_char_check = document.getElementById("64-char-check");
    let one_letter_check = document.getElementById("one-letter-check");
    let one_digit_check = document.getElementById("one-digit-check");
    let char_type_check = document.getElementById("char-type-check");

    let blue_bar = document.getElementById("blue-bar");
    let green_bar = document.getElementById("green-bar");
    let yellow_bar = document.getElementById("yellow-bar");

    let pass_strength_text = document.getElementById("pass-strength-text");

    let repeat_inputted = false;

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

    nick_field.addEventListener("focusout", ()=> {
        if (4 <= nick_field.value.length && nick_field.value.length <= 64 && !nick_field.className.includes("filled")) {
            nick_field.className += " filled";
            return;
        }

        if (!nick_field.className.includes("incorrect")) {
            nick_field.className += " incorrect";
        }
    });

    function refresh_password_fields() {
        /*PASSWORD FIELD*/
        password_field.className = password_field.className.replaceAll(" incorrect", "")
            .replaceAll(" filled", "");

        if (pass_regex.test(password_field.value) && !password_field.className.includes("filled")) {
            password_field.className += " filled";
        }else if (!password_field.className.includes("incorrect")){
            password_field.className += " incorrect";
        }

        /*REPEAT FIELD*/
        repeat_field.className = repeat_field.className.replaceAll(" incorrect", "")
            .replaceAll(" filled", "");
        if (password_field.value === repeat_field.value && password_field.className.includes(" filled") && !repeat_field.className.includes("filled")) {
            repeat_field.className += " filled";
        }else if (!repeat_field.className.includes(" incorrect") && repeat_inputted) {
            repeat_field.className += " incorrect";
        }
    }

    password_field.addEventListener("focusout", ()=>{
        refresh_password_fields();
    });

    password_field.addEventListener("input", ()=>{
        let value = password_field.value;

        if (value.length >= 8 && !min_char_check.className.includes("correct")) {
            min_char_check.className += " correct";
        } else if (8 > value.length) {
            min_char_check.className = min_char_check.className.replaceAll(" correct", "");
        }

        if (value.length <= 64 && !max_char_check.className.includes("correct")) {
            max_char_check.className += " correct";
        } else if (64 < value.length) {
            max_char_check.className = max_char_check.className.replaceAll(" correct", "");
        }

        const any_letter_regex = RegExp("(?=.*[a-zA-Z])");
        const any_digit_regex = RegExp("(?=.*[0-9])");
        const char_regex = new RegExp("^[a-zA-Z0-9.!@#$%&*]*$");

        if (any_letter_regex.test(value) && !one_letter_check.className.includes("correct")) {
            one_letter_check.className += " correct";
        } else if (!any_letter_regex.test(value)) {
            one_letter_check.className = one_letter_check.className.replaceAll(" correct", "");
        }

        if (any_digit_regex.test(value) && !one_digit_check.className.includes("correct")) {
            one_digit_check.className += " correct";
        } else if (!any_digit_regex.test(value)) {
            one_digit_check.className = one_digit_check.className.replaceAll(" correct", "");
        }

        if (char_regex.test(value) && !char_type_check.className.includes("correct")) {
            char_type_check.className += " correct";
        } else if (!char_regex.test(value)) {
            char_type_check.className = char_type_check.className.replaceAll(" correct", "");
        }

        const num_sym_up_regex = new RegExp("(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[.!@#$%&*])");
        const num_up_regex = new RegExp("(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])");
        const num_or_up_regex = new RegExp("(?=.*[a-z])(?=.*[A-Z0-9])");

        let points = 0;

        if (num_sym_up_regex.test(value)) {
            if (value.length >= 10) {
                points = 3;
            } else if (value.length >= 9) {
                points = 2;
            } else if (value.length >= 8) {
                points = 1;
            }
        } else if (num_up_regex.test(value)) {
            if (value.length >= 11) {
                points = 3;
            } else if (value.length >= 10){
                points = 2;
            }  else if (value.length >= 9){
                points = 1;
            }
        } else if (num_or_up_regex.test(value)) {
            if (value.length >= 12) {
                points = 3;
            } else if (value.length >= 11){
                points = 2;
            }  else if (value.length >= 10){
                points = 1;
            }
        } else {
            if (value.length > 12) {
                points = 2;
            } else if (value.length > 11) {
                points = 1;
            }
        }

        if (points === 0) {
            pass_strength_text.innerText = "Very weak";
            pass_strength_text.style.color = "rgba(229, 102, 63, 0.7)";
        }

        if (points >= 1) {
            yellow_bar.style.display = "block";
            pass_strength_text.innerText = "Weak";
            pass_strength_text.style.color = "rgba(229, 188, 63, 0.7)";
        } else {
            yellow_bar.style.display = "none";
        }

        if (points >= 2) {
            green_bar.style.display = "block";
            pass_strength_text.innerText = "Strong";
            pass_strength_text.style.color = "rgba(99, 229, 63, 0.7)";
        } else {
            green_bar.style.display = "none";
        }

        if (points === 3) {
            blue_bar.style.display = "block";
            pass_strength_text.innerText = "Very strong";
            pass_strength_text.style.color = "rgba(58, 143, 234, 0.7)";
        } else {
            blue_bar.style.display = "none";
        }
    });

    repeat_field.addEventListener("input", ()=>{
        repeat_inputted = true;
    })

    repeat_field.addEventListener("focusout", ()=>{
        repeat_inputted = true;
        refresh_password_fields();
    });
});