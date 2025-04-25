document.body.addEventListener("click", (ev) => {
    const isTitleBar = !!ev.target.closest(".plan__title-bar");
    const planWrapper = ev.target.closest(".plan");

    if (!isTitleBar) return;
    if (!planWrapper) return;

    planWrapper.classList.toggle("plan--open");
});