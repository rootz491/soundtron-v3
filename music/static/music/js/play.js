console.log('loaded javascript file successfully.')

const audio = document.querySelector('audio');
const links = document.querySelectorAll(".song");


console.log(links);

// for-of loop
// gives us a constant value for each "link" in our list of links:

for (const link of links) {
    console.log(link);
    // we can then use this link and add an event listener:
    link.addEventListener("click", setSong);
}



function setSong(e) {
//    console.log('clicked')

    if(e.target.classList == 'play') {
        let playBtn = e.target;

        //  close all buttons
        closeAllMusic();
        //  switch to other button
        song = playBtn.parentElement;
        let stopBtn = song.querySelector('.stop');
        stopBtn.hidden = false;
        playBtn.hidden = true;
        //  work with audio
        audio.src = song.dataset.key;
        audio.load();
        audio.play();
    }
    else if(e.target.classList == 'stop') {
        let stopBtn = e.target;

        //  switch to other button
        song = stopBtn.parentElement;
        let playBtn = song.querySelector('.play');
        playBtn.hidden = false;
        stopBtn.hidden = true;
        //  work with audio
        audio.pause();
    }
}


function closeAllMusic() {
    allPlay = document.querySelectorAll('.play');
    allStop = document.querySelectorAll('.stop');

    allPlay.forEach(btn => btn.hidden = false);
    allStop.forEach(btn => btn.hidden = true);

}