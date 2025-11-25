document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("theme-toggle");

    if (!btn) {
        console.error("Кнопка переключения темы не найдена!");
        return;
    }

    btn.addEventListener("click", function () {
        document.body.classList.toggle("dark-theme");
        document.body.classList.toggle("light-theme");

        if (document.body.classList.contains("dark-theme")) {
            btn.textContent = "☀️";
        } else {
            btn.textContent = "🌙";
        }
    });
});
