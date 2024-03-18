function typeWriter(elementId, text, typingSpeed, delayAfter) {
    let i = 0;
    const element = document.getElementById(elementId);
    element.innerHTML = "";

    function typing() {
        if (i < text.length) {
            element.innerHTML += text.charAt(i);
            i++;
            setTimeout(typing, typingSpeed);
        } else {
            setTimeout(() => typeWriter(elementId, text, typingSpeed, delayAfter), delayAfter);
        }
    }
    typing();
}

const text = "Hello, World!";
const typingSpeed = 150;
const delayAfter = 2000;

document.addEventListener("DOMContentLoaded", function() {
    typeWriter("typing", text, typingSpeed, delayAfter);
});