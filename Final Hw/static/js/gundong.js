const specificContent = document.getElementById('hotspot');
let ul=document.querySelector('ul')
ul.innerHTML=ul.innerHTML+ul.innerHTML;
let lis=document.querySelectorAll('li');
let btns=document.querySelectorAll('.btn');
let spq=-2;
ul.style.width=lis[0].offsetWidth*lis.length+'px';
function move()
{
    if(ul.offsetLeft<-ul.offsetWidth/4)
    {
        ul.style.left='0';
    }
    if(ul.offsetLeft>0)
    {
        ul.style.left=-ul.offsetWidth/4+'px';

    }
    ul.style.left=ul.offsetLeft+spa+'px';
}
let timer=setInterval(move,1000);
ul.addEventListener('mousemove',function(){
    clearInterval(timer);
})
ul.addEventListener('mouseout',function(){timer=setInterval(move,1000)})
btns[0].addEventListener('click',function(){spa=-2})
btns[1].addEventListener('click',function(){spa=2})