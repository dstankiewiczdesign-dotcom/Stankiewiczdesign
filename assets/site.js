/* Shared behaviour for every page: mobile menu, copy e-mail, contact form.
   Each language has its own pages, so the language comes from <html lang> and paths from data-root. */
(function(){
const lang=document.documentElement.lang==="pl"?"pl":"en";
const root=document.body.dataset.root||"";
const UI={pl:{copied:"Skopiowano",sending:"Wysyłam…",done:"Wysłane",thanks:"Dziękuję, wiadomość została wysłana. Odpowiem najszybciej, jak to możliwe.",missing:"Uzupełnij zaznaczone pola.",fail:"Nie udało się wysłać. Otwieram Twój program pocztowy z gotową wiadomością.",subject:"Zapytanie ze strony: "},
en:{copied:"Copied",sending:"Sending…",done:"Sent",thanks:"Thank you, your message has been sent. I will reply as soon as I can.",missing:"Please fill in the marked fields.",fail:"Could not send. Opening your mail app with the message ready.",subject:"Enquiry from the website: "}}[lang];
const done=document.getElementById("done");

/* mobile menu */
const navEl=document.querySelector("nav"),menuBtn=document.querySelector(".menu-btn");
if(menuBtn){
  const setOpen=o=>{navEl.classList.toggle("open",o);menuBtn.setAttribute("aria-expanded",o)};
  menuBtn.onclick=()=>setOpen(!navEl.classList.contains("open"));
  document.getElementById("menu").addEventListener("click",e=>{if(e.target.closest("a"))setOpen(false)});
  addEventListener("keydown",e=>{if(e.key==="Escape"&&navEl.classList.contains("open")){setOpen(false);menuBtn.focus()}});
}
function flash(text){if(!done)return;done.textContent=text;done.classList.add("on");setTimeout(()=>done.classList.remove("on"),2600)}

const copy=document.getElementById("copy");
if(copy)copy.onclick=async e=>{const m=document.getElementById("mail");try{await navigator.clipboard.writeText(m.textContent);e.target.textContent=UI.copied}catch(_){const r=document.createRange();r.selectNodeContents(m);getSelection().removeAllRanges();getSelection().addRange(r)}};

const form=document.getElementById("form");
if(form){
  const note=document.getElementById("form-note"),send=document.getElementById("send");
  const fields=[...form.querySelectorAll("[required]")];
  form.noValidate=true;
  fields.forEach(f=>f.addEventListener("input",()=>{if(f.checkValidity())f.removeAttribute("aria-invalid")}));
  form.addEventListener("submit",async e=>{
    e.preventDefault();if(form._honey.value)return;
    const bad=fields.filter(f=>!f.checkValidity());
    fields.forEach(f=>bad.includes(f)?f.setAttribute("aria-invalid","true"):f.removeAttribute("aria-invalid"));
    if(bad.length){note.textContent=UI.missing;bad[0].focus();return}
    const fd=new FormData(form),f=Object.fromEntries(fd);
    note.textContent=UI.sending;send.disabled=true;
    try{
      const r=await fetch(root+"kontakt.php",{method:"POST",body:fd,headers:{Accept:"application/json"}});
      const j=await r.json();if(!r.ok||!j.ok)throw 0;
      form.reset();note.textContent=UI.thanks;flash(UI.done);
    }catch(_){
      note.textContent=UI.fail;
      location.href="mailto:studio@stankiewicz.design?subject="+encodeURIComponent(UI.subject+f.name+" ("+f.type+")")+"&body="+encodeURIComponent(f.message+"\n\n"+f.name+" · "+f.email);
    }finally{send.disabled=false}
  });
}
})();
