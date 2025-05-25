document.addEventListener("DOMContentLoaded", () => {
  const startButton = document.getElementById("start-emulation");

  // Пример маршрута (Можешь изменить координаты)
  const route = [
      [55.751244, 37.618423],
      [55.752000, 37.619000],
      [55.753000, 37.620000],
      [55.754000, 37.621000],
      [55.755000, 37.622000]
  ];

  let currentIndex = 0;
  const droneId = 1;  // Укажи реальный ID дрона в базе

  startButton.addEventListener("click", () => {
      const interval = setInterval(() => {
          if (currentIndex >= route.length) {
              clearInterval(interval);
              console.log("Эмуляция завершена");
              return;
          }

          const [latitude, longitude] = route[currentIndex];
          console.log(`Обновление координат: ${latitude}, ${longitude}`);

          fetch(`/api/dronelocations/`, {
              method: "POST",
              headers: {
                  "Content-Type": "application/json",
              },
              body: JSON.stringify({
                  drone: droneId,
                  location: {
                      type: "Point",
                      coordinates: [longitude, latitude]
                  }
              })
          })
          .then(response => {
              if (!response.ok) {
                  console.error("Ошибка при отправке координат");
              }
          });

          currentIndex++;
      }, 1000);
  });
});