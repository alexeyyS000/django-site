function timeEnd() {
  localStorage.removeItem('{{test_number}}');
  location.replace("{% url 'polls:result' test_number %}")
}

function setTime() {
  localStorage.setItem('{{test_number}}', time);
}


function UpdateTimer(){
    const minutes = Math.floor(time / 60);
    let seconds = time % 60;
    seconds = seconds < 10 ? "0" + seconds:seconds;
    countDown.innerHTML = `${minutes}:${seconds}`;
    if (time <= 0){timeEnd();}
    time--;
}


let time = localStorage.getItem('{{test_number}}');
if (time == null) {time =  Number('{{time_for_complete}}');}


const countDown = document.getElementById('Timer');
setInterval(UpdateTimer, 1000)
