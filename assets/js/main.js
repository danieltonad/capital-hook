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
