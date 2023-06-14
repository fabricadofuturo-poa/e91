let reiniciar = document.getElementById("reiniciar");
let contador = document.getElementById("contador");
contador.innerHTML = "";
//~ let cd = document.createElement("span");
//~ cd.className = "badge rounded-pill text-bg-light";
//~ contador.appendChild(cd);
let ch = document.createElement("div");
ch.className = "col fs-1 text-light";
contador.appendChild(ch);
let cm = document.createElement("div");
cm.className = "col fs-1 text-light";
contador.appendChild(cm);
let cs = document.createElement("div");
cs.className = "col fs-1 text-light";
contador.appendChild(cs);

let x = setInterval(function() {
  let now = new Date();
  let distance = contagem.getTime() - now.getTime();
  //~ let days = Math.floor(distance / (1000 * 60 * 60 * 24));
  let hours = Math.floor(
    (distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  let minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  let seconds = Math.floor((distance % (1000 * 60)) / 1000);
  if (distance <= 0) {
    clearInterval(x);
    contador.className = "row bg-warning";
    contador.innerHTML = "TERMINOU&excl;";
  } else {
    //~ if (days > 0) {
      //~ cd.innerHTML = days;
    //~ } else {
      //~ cd.innerHTML = "";
    //~ }
    if (hours > 0) {
      ch.innerHTML = (hours + "").padStart(2, "0") + " :";
    } else if (
      //~ days <= 0 &&
      hours <= 0
    ) {
      ch.innerHTML = "";
    }
    if (minutes > 0) {
      cm.innerHTML = (minutes + "").padStart(2, "0") + " :";
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
  contador.className = "row bg-success";
  contagem.setTime(
    resetNow.getTime() +
    //~ (document.getElementById("dias").value * 24 * 60 * 60 * 1000) + 
    (document.getElementById("horas").value * 60 * 60 * 1000) + 
    (document.getElementById("minutos").value * 60 * 1000) + 
    (document.getElementById("segundos").value * 1000)
  );
  //~ contagem.setFullYear(resetNow.getFullYear());
  //~ console.log(
    //~ "anos",
    //~ resetNow.getFullYear(),
    //~ "+ 0",
    //~ contagem.getFullYear(),
  //~ );
  //~ contagem.setMonth(resetNow.getMonth());
  //~ console.log(
    //~ "meses",
    //~ resetNow.getMonth(),
    //~ "+ 0",
    //~ contagem.getMonth(),
  //~ );
  //~ contagem.setDate(resetNow.getDate() + 
    //~ document.getElementById("dias").value);
  //~ console.log(
    //~ "dias",
    //~ resetNow.getDate(),
    //~ "+ " + document.getElementById("dias").value,
    //~ contagem.getDate(),
  //~ );
  //~ contagem.setHours(resetNow.getHours() + 
    //~ document.getElementById("horas").value);
  //~ console.log(
    //~ "horas",
    //~ resetNow.getHours(),
    //~ "+ " + document.getElementById("horas").value,
    //~ contagem.getHours(),
  //~ );
  //~ contagem.setMinutes(resetNow.getMinutes() + 
    //~ document.getElementById("minutos").value);
  //~ console.log(
    //~ "minutos",
    //~ resetNow.getMinutes(),
    //~ "+ " + document.getElementById("minutos").value,
    //~ contagem.getMinutes(),
  //~ );
  //~ contagem.setSeconds(resetNow.getSeconds() + 
    //~ document.getElementById("segundos").value);
  //~ console.log(
    //~ "segundos",
    //~ resetNow.getSeconds(),
    //~ "+ " + document.getElementById("segundos").value,
    //~ contagem.getSeconds(),
  //~ );
}
