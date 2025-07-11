// Import Lucide library
document.addEventListener("DOMContentLoaded", function () {
  const lucideScript = document.createElement("script");
  lucideScript.src = "https://unpkg.com/lucide@latest";
  lucideScript.onload = function () {
    lucide.createIcons();
    console.log("Lucide icons initialized");
  };

  document.head.appendChild(lucideScript);
});


document.body.addEventListener('htmx:afterSwap', function(evt) {
  if(evt.target.id === "payload-response") {
    navigator.clipboard.writeText(evt.target.innerText);
    showToast("Payload copied to clipboard");
  }
});


function showToast(message) {
  const toast = document.querySelector('.notify-toast');
  const notifyText = document.querySelector('.notify-text');
  notifyText.textContent = message;
  toast.classList.add('show');

  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}