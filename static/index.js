var countDownDate = new Date("Apr 1, 2024 16:20:00");
let reiniciar = document.getElementById("reiniciar");
let contador = document.getElementById("contador");
contador.innerHTML = "";
//~ let cd = document.createElement("span");
//~ cd.className = "badge rounded-pill text-bg-light";
//~ contador.appendChild(cd);
let ch = document.createElement("span");
ch.className = "badge rounded-pill text-bg-light";
contador.appendChild(ch);
let cm = document.createElement("span");
cm.className = "badge rounded-pill text-bg-light";
contador.appendChild(cm);
let cs = document.createElement("span");
cs.className = "badge rounded-pill text-bg-light";
contador.appendChild(cs);

let x = setInterval(function() {
  let now = new Date();
  let distance = countDownDate.getTime() - now.getTime();
  //~ let days = Math.floor(distance / (1000 * 60 * 60 * 24));
  let hours = Math.floor(
    (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  let seconds = Math.floor((distance % (1000 * 60)) / 1000);
  if (distance <= 0) {
    clearInterval(x);
    contador.className = "btn btn-warning";
    contador.innerHTML = "TERMINOU&excl;";
  } else {
    //~ if (days > 0) {
      //~ cd.innerHTML = days;
    //~ } else {
      //~ cd.innerHTML = "";
    //~ }
    if (hours > 0) {
      ch.innerHTML = (hours + "").padStart(2, "0");
    } else if (
      //~ days <= 0 &&
      hours <= 0
    ) {
      ch.innerHTML = "";
    }
    if (minutes > 0) {
      cm.innerHTML = (minutes + "").padStart(2, "0");
    } else if (
      //~ days <= 0 &&
      hours <= 0 &&
      minutes <= 0
    ) {
      cm.innerHTML = "";
    }
    if (seconds > 0) {
      cs.innerHTML = (seconds + "").padStart(2, "0");
    } else if (
      //~ days <= 0 &&
      hours <= 0 &&
      minutes <= 0 &&
      seconds <= 0
    ) {
      cs.innerHTML = "";
    }
  }
}, 1000);

reiniciar.onclick = function resetTime() {
  let resetNow = new Date();
  contador.innerHTML = "";
  //~ contador.appendChild(cd);
  contador.appendChild(ch);
  contador.appendChild(cm);
  contador.appendChild(cs);
  contador.className = "btn btn-success";
  countDownDate.setTime(
    resetNow.getTime() +
    //~ (document.getElementById("dias").value * 24 * 60 * 60 * 1000) + 
    (document.getElementById("horas").value * 60 * 60 * 1000) + 
    (document.getElementById("minutos").value * 60 * 1000) + 
    (document.getElementById("segundos").value * 1000)
  );
  //~ countDownDate.setFullYear(resetNow.getFullYear());
  //~ console.log(
    //~ "anos",
    //~ resetNow.getFullYear(),
    //~ "+ 0",
    //~ countDownDate.getFullYear(),
  //~ );
  //~ countDownDate.setMonth(resetNow.getMonth());
  //~ console.log(
    //~ "meses",
    //~ resetNow.getMonth(),
    //~ "+ 0",
    //~ countDownDate.getMonth(),
  //~ );
  //~ countDownDate.setDate(resetNow.getDate() + 
    //~ document.getElementById("dias").value);
  //~ console.log(
    //~ "dias",
    //~ resetNow.getDate(),
    //~ "+ " + document.getElementById("dias").value,
    //~ countDownDate.getDate(),
  //~ );
  //~ countDownDate.setHours(resetNow.getHours() + 
    //~ document.getElementById("horas").value);
  //~ console.log(
    //~ "horas",
    //~ resetNow.getHours(),
    //~ "+ " + document.getElementById("horas").value,
    //~ countDownDate.getHours(),
  //~ );
  //~ countDownDate.setMinutes(resetNow.getMinutes() + 
    //~ document.getElementById("minutos").value);
  //~ console.log(
    //~ "minutos",
    //~ resetNow.getMinutes(),
    //~ "+ " + document.getElementById("minutos").value,
    //~ countDownDate.getMinutes(),
  //~ );
  //~ countDownDate.setSeconds(resetNow.getSeconds() + 
    //~ document.getElementById("segundos").value);
  //~ console.log(
    //~ "segundos",
    //~ resetNow.getSeconds(),
    //~ "+ " + document.getElementById("segundos").value,
    //~ countDownDate.getSeconds(),
  //~ );
}
