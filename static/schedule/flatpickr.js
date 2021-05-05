window.addEventListener("load", () =>
    flatpickr("#datetime-picker", {
        enableTime: true,
        dateFormat: "Y-m-d H:i",
        altInput: true,
        altFormat: "F j, Y at h:i K",
        minDate: "today",
    })
);
