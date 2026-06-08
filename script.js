

    const faders = document.querySelectorAll(".fade-in");

    const appearOnScroll = new IntersectionObserver(
    function (entries, observer) {
        entries.forEach(entry => {
        if (!entry.isIntersecting) return;

        entry.target.classList.add("show");
        observer.unobserve(entry.target);
        });
    },
    {
        threshold: 0.2
    }
    );

    faders.forEach(fader => {
    appearOnScroll.observe(fader);
    });
    document.addEventListener("DOMContentLoaded", () => {

    const aboutCard = document.querySelector(".about-card");

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if(entry.isIntersecting){
                aboutCard.classList.add("show");
            }
        });
    }, {
        threshold: 0.2
    });

    observer.observe(aboutCard);

});
const skillCards = document.querySelectorAll(".skill-card");

const skillObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {

        if(entry.isIntersecting){
            entry.target.classList.add("show");
        }

    });
},{
    threshold: 0.15
});

skillCards.forEach(card => {
    skillObserver.observe(card);
});
const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".nav-links a");

window.addEventListener("scroll", () => {

    let current = "";

    sections.forEach(section => {

        const sectionTop = section.offsetTop - 150;
        const sectionHeight = section.clientHeight;

        if (window.scrollY >= sectionTop) {
            current = section.getAttribute("id");
        }

    });

    navLinks.forEach(link => {

        link.classList.remove("active");

        if (link.getAttribute("href") === "#" + current) {
            link.classList.add("active");
        }

    });

});
const timelineItems = document.querySelectorAll(".timeline-item");

const educationObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if(entry.isIntersecting){
            entry.target.classList.add("show");
        }
    });
},{
    threshold: 0.15
});

timelineItems.forEach(item => {
    educationObserver.observe(item);
});
const projectCards = document.querySelectorAll(".project-card");

const projectObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if(entry.isIntersecting){
            entry.target.classList.add("show");
        }
    });
},{
    threshold: 0.15
});

projectCards.forEach(card => {
    projectObserver.observe(card);
});
const contactElements = document.querySelectorAll(
    ".contact-form, .contact-info"
);

const contactObserver = new IntersectionObserver((entries)=>{
    entries.forEach(entry=>{
        if(entry.isIntersecting){
            entry.target.classList.add("show");
        }
    });
},{
    threshold: 0.2
});

contactElements.forEach(el=>{
    contactObserver.observe(el);
});
 document.addEventListener("DOMContentLoaded", () => {

        const texts = [
            "Full Stack Developer",
            "Frontend Developer",
            "Backend Developer",
            "Problem Solver",
            "UI/UX Enthusiast"
        ];

        let textIndex = 0;
        let charIndex = 0;
        let isDeleting = false;

        const typingElement = document.getElementById("typing");

        function type() {

            const currentText = texts[textIndex];

            if (!isDeleting) {
                typingElement.textContent =
                    currentText.substring(0, charIndex + 1);
                charIndex++;

                if (charIndex === currentText.length) {
                    isDeleting = true;
                    setTimeout(type, 1500);
                    return;
                }
            } else {
                typingElement.textContent =
                    currentText.substring(0, charIndex - 1);
                charIndex--;

                if (charIndex === 0) {
                    isDeleting = false;
                    textIndex = (textIndex + 1) % texts.length;
                }
            }

            setTimeout(type, isDeleting ? 50 : 100);
        }

        type();
    });
     const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {

            if(entry.isIntersecting){
                entry.target.classList.add("show");
            }

        });
    },{
        threshold: 0.2
    });

    document.querySelectorAll(".about-card").forEach((el)=>{
        observer.observe(el);
    });

    const form = document.getElementById("contact-form");

    form.addEventListener("submit", function(e){

        e.preventDefault();

        emailjs.sendForm(
            "service_alpqn7l",
            "template_fqrjwz9",
            this
        )
        .then(() => {

            alert("Message sent successfully!");

            form.reset();

        })
        .catch((error) => {

            console.error(error);

            alert("Failed to send message.");

        });

    });
    
