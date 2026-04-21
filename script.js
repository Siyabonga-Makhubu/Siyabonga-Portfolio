const texts = [
    "I build web apps",
    "I solve problems",
    "I code ideas"
];

let index = 0;
let charIndex = 0;
let isDeleting = false;

/* =========================
   TYPEWRITER EFFECT
========================= */
function typeEffect() {
    const typingElement = document.getElementById("typing");
    if (!typingElement) return;

    const currentText = texts[index];

    if (isDeleting) {
        typingElement.textContent = currentText.substring(0, charIndex--);
    } else {
        typingElement.textContent = currentText.substring(0, charIndex++);
    }

    let speed = isDeleting ? 80 : 140;

    if (!isDeleting && charIndex === currentText.length) {
        speed = 1500;
        isDeleting = true;
    } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        index = (index + 1) % texts.length;
        speed = 500;
    }

    setTimeout(typeEffect, speed);
}

/* =========================
   DOM READY
========================= */
window.addEventListener("DOMContentLoaded", function () {

    /* START TYPE EFFECT */
    typeEffect();

    /* INIT EMAILJS */
    emailjs.init("mr_sgh8OY1KQQWCV3");

    /* =========================
       DOWNLOAD POPUP
    ========================= */
    const downloadBtn = document.getElementById("downloadBtn");
    const popup = document.getElementById("downloadPopup");

    if (downloadBtn && popup) {
        downloadBtn.addEventListener("click", () => {
            popup.classList.add("show");

            setTimeout(() => {
                popup.classList.remove("show");
            }, 2000);
        });
    }

    /* =========================
       CONTACT FORM EMAILJS
    ========================= */
    const form = document.getElementById("contact-form");

    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();

            emailjs.send("service_alpqn7l", "template_fqrjwz9", {
                user_name: document.getElementById("user_name").value,
                user_email: document.getElementById("user_email").value,
                title: document.getElementById("title").value,
                message: document.getElementById("message").value
            })
            .then(() => {
                alert("Message sent successfully!");
                form.reset();
            })
            .catch((error) => {
                console.log("EmailJS Error:", error);
                alert("Failed to send message.");
            });
        });
    }

});