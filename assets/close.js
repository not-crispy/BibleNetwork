// (function() {
//     if (window.addEventListener) {
//         window.addEventListener("load", loadHandler, false);
//     }
//     else if (window.attachEvent) {
//         window.attachEvent("onload", loadHandler);
//     }
//     else {
//         window.onload = loadHandler; // Or you may want to leave this off and just not support REALLY old browsers
//     }

//     function loadHandler() {
//         setTimeout(doMyStuff, 0);
//     }

//     function doMyStuff() {
//             // Select the element with the id "box"
//         const box = document.getElementById('info-box-wrapper');
//         const graph = document.getElementById('graph');

//         // Add a touch event listener to detect the tap
//         console.log("close.js activated!")
//         box.addEventListener('touchend', function() {
//         // Change the style to hide the element
//         box.style.display = 'none';
//         });
//     }
// })();