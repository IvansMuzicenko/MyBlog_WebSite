//---------------------START OF LOGO COLOR CHANGE
let colRand = () => Math.floor(Math.random() * 256);

const siteNames = document.querySelectorAll(".colRandom");
// let firstHalf = document.querySelector(".firstHalf");
// let secondHalf = document.querySelector(".secondHalf");

// let colArr = [`rgb(23, 54, 216)`, `rgb(178,202,18)`];

let changeColor = () => {
    for (siteName of siteNames) {
        let r = colRand();
        let g = colRand();
        let b = colRand();

        siteName.style.color = `rgb(${r},${g},${b})`;

        // firstHalf.style.color = `${colArr[0]}`;
        // secondHalf.style.color = `${colArr[1]}`;

        // transition is not working when styles are rewriten, but not added
        // siteName.style = `background: linear-gradient(${colArr[0]},${colArr[1]}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; `;
        // colArr.push(`rgb(${r},${g},${b})`);
        // colArr.shift();

    }
};
changeColor();
setInterval(changeColor, 1000);


//-------------------END OF LOGO COLOR CHANGE
//---------------------START OF THEME CHANGE

const themeChange = document.querySelector(".themeChange");

let mainNav = document.querySelector("#mainNav");
let logoBG = document.querySelector('#logoBG');


lightTheme.addEventListener('click', () => {
    switchThemeFunc("light", "dark");
});

darkTheme.addEventListener('click', () => {
    switchThemeFunc("dark", "light");
});

let switchThemeFunc = (current, opposite) => {
    const currentElements = document.querySelectorAll(`[class*='bg-${current}']`);
    const oppositeElements = document.querySelectorAll(`[class*='bg-${opposite}']`);
    themeChange.className = "";
    themeChange.classList.add(`text-${opposite}`);
    mainNav.classList.remove(`navbar-${current}`);
    mainNav.classList.add(`navbar-${opposite}`);
    document.body.classList.remove(`navbar-${current}`);
    document.body.classList.add(`navbar-${opposite}`);

    for (curEl of currentElements) {
        curEl.classList.remove(`bg-${current}`);
        curEl.classList.add(`bg-${opposite}`);
    };

    for (curEl of oppositeElements) {
        curEl.classList.remove(`bg-${opposite}`);
        curEl.classList.add(`bg-${current}`);
    };

};
//---------------------END  OF THEME CHANGE

