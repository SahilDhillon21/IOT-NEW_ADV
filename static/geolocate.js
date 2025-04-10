// Detect if device is mobile
function isMobileDevice() {
  return /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
}

async function fetchSensorData() {
  const res = await fetch("/data");
  const data = await res.json();
  document.getElementById("temp").textContent = data.temperature ?? "N/A";
  document.getElementById("humidity").textContent = data.humidity ?? "N/A";
  document.getElementById("latitude").textContent = data.latitude ?? "N/A";
  document.getElementById("longitude").textContent = data.longitude ?? "N/A";
}

function updateLocation() {
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
          console.log("Location sent:", latitude, longitude);
        } catch (error) {
          console.error("Failed to send location:", error);
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
  setInterval(fetchSensorData, 2000);
  setInterval(updateLocation, 2000);
};
