async function fetchSensorData() {
  const res = await fetch("/data");
  const data = await res.json();

  const temp = data.temperature;
  const humidity = data.humidity;

  document.getElementById("temp").textContent = temp !== undefined ? temp + " ℃" : "N/A";
  document.getElementById("humidity").textContent = humidity !== undefined ? humidity + "%" : "N/A";
  document.getElementById("latitude").textContent = data.latitude ?? "N/A";
  document.getElementById("longitude").textContent = data.longitude ?? "N/A";
  document.getElementById("last_updated").textContent = data.timestamp ?? "N/A";
  document.getElementById("package_id").textContent = data.package_id ?? "N/A";

  // Show alert if temperature or humidity crosses threshold
  const alertBox = document.getElementById("live-alert");
  const alertMessage = document.getElementById("live-alert-message");

  if ((temp !== undefined && temp > 40) || (humidity !== undefined && humidity > 65)) {
    let messages = [];
    if (temp > 40) messages.push(`🔥 High Temperature: ${temp} ℃`);
    if (humidity > 65) messages.push(`💧 High Humidity: ${humidity}%`);

    alertMessage.innerHTML = messages.join("<br>");
    alertBox.style.display = "block";
  } else {
    alertBox.style.display = "none";
  }
}


function updateLocation() {
  // Detect if device is mobile
  function isMobileDevice() {
    return /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
  }
  if (!isMobileDevice()) {
    return;
  }

  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;

        try {
          await fetch("/update", {
            method: "POST",
            headers: {
              "Content-Type": "application/json"
            },
            body: JSON.stringify({ latitude, longitude })
          });
        } catch (error) {
        }
      },
      (error) => {
        console.warn("Geolocation error:", error);
      },
      { enableHighAccuracy: true }
    );
  } else {
    console.log("Geolocation not supported.");
  }
}

window.onload = () => {
  fetchSensorData();
  updateLocation();
  setInterval(fetchSensorData, 3000);
  setInterval(updateLocation, 3000);
};
