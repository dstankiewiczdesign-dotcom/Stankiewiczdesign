/* Shared behaviour for every page: copy e-mail, contact form, newsletter, Instagram feed, hero slideshow.
   Each language has its own pages now, so the language comes from <html lang> and paths from data-root. */
(function(){
const lang=document.documentElement.lang==="pl"?"pl":"en";
const root=document.body.dataset.root||"";
const UI={pl:{copied:"Skopiowano",sending:"Wysyłam…",done:"Wysłane",subscribed:"Zapisane",fail_nl:"Nie udało się zapisać. Spróbuj ponownie za chwilę.",ig_empty:"Posty z Instagrama pojawią się tutaj.",ig_alt:"Post na Instagramie",fail:"Nie udało się wysłać. Otwieram Twój program pocztowy z gotową wiadomością.",subject:"Zapytanie ze strony: "},
en:{copied:"Copied",sending:"Sending…",done:"Sent",subscribed:"Subscribed",fail_nl:"Could not subscribe. Please try again in a moment.",ig_empty:"Instagram posts will appear here.",ig_alt:"Instagram post",fail:"Could not send. Opening your mail app with the message ready.",subject:"Enquiry from the website: "}}[lang];
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
  form.addEventListener("submit",async e=>{
    e.preventDefault();if(form._honey.value)return;
    const fd=new FormData(form),f=Object.fromEntries(fd);
    note.textContent=UI.sending;send.disabled=true;
    try{
      const r=await fetch(root+"kontakt.php",{method:"POST",body:fd,headers:{Accept:"application/json"}});
      const j=await r.json();if(!r.ok||!j.ok)throw 0;
      form.reset();note.textContent="";flash(UI.done);
    }catch(_){
      note.textContent=UI.fail;
      location.href="mailto:studio@stankiewicz.design?subject="+encodeURIComponent(UI.subject+f.name+" ("+f.type+")")+"&body="+encodeURIComponent(f.message+"\n\n"+f.name+" · "+f.email);
    }finally{send.disabled=false}
  });
}

const nl=document.getElementById("nl");
if(nl){
  const nlNote=document.getElementById("nl-note"),nlSend=document.getElementById("nl-send");
  nl.addEventListener("submit",async e=>{
    e.preventDefault();if(nl._honey.value)return;
    const fd=new FormData(nl);fd.append("lang",lang);nlNote.textContent=UI.sending;nlSend.disabled=true;
    try{const r=await fetch(root+"newsletter.php",{method:"POST",body:fd,headers:{Accept:"application/json"}});const j=await r.json();if(!r.ok||!j.ok)throw 0;
      nl.reset();nlNote.textContent="";flash(UI.subscribed);
    }catch(_){nlNote.textContent=UI.fail_nl}finally{nlSend.disabled=false}
  });
}

/* instagram: posts come from a Behold.so feed of the studio account */
const IG_FEED="https://feeds.behold.so/K7NfVXLiMDaQ8rR1hte4";
const ig=document.getElementById("ig");
if(ig)(async()=>{
  try{const r=await fetch(IG_FEED);const d=await r.json();const posts=(Array.isArray(d)?d:d.posts||[]).slice(0,8);
    if(!posts.length){ig.innerHTML=`<p class="empty">${UI.ig_empty}</p>`;return}
    ig.innerHTML=posts.map(p=>{const src=(p.sizes&&p.sizes.medium&&p.sizes.medium.mediaUrl)||(p.mediaType==="VIDEO"?p.thumbnailUrl:p.mediaUrl);const alt=(p.prunedCaption||p.caption||UI.ig_alt).slice(0,120).replace(/"/g,"&quot;");return `<a href="${p.permalink}" target="_blank" rel="noopener"><img src="${src}" alt="${alt}" loading="lazy"></a>`}).join("");
  }catch(_){ // feed JSON unreachable: fall back to Behold's own widget
    ig.innerHTML='<behold-widget feed-id="K7NfVXLiMDaQ8rR1hte4" style="grid-column:1/-1"></behold-widget>';
    const sc=document.createElement("script");sc.type="module";sc.src="https://w.behold.so/widget.js";document.head.append(sc);
  }
})();

/* hero slideshow: one frame per project, crossfade every 6 s; extra frames load after the page */
const box=document.getElementById("slides");
if(box){
  const S=JSON.parse(box.dataset.slides),dots=document.getElementById("dots"),sname=document.getElementById("slide-name");
  let added=false;const addSlides=()=>{if(added)return;added=true;S.slice(1).forEach(s=>{const im=new Image();im.src=root+s.src;im.alt="";im.width=1402;im.height=1122;box.append(im)})};
  if(document.readyState==="complete")addSlides();else addEventListener("load",addSlides);
  dots.innerHTML=S.map(s=>`<button type="button" aria-label="${s.name}"></button>`).join("");
  let cur=0,timer;
  const show=i=>{
    if(i!==0)addSlides();const imgs=box.children,bs=dots.children;
    imgs[cur].classList.remove("on");bs[cur].classList.remove("on");
    cur=(i+S.length)%S.length;imgs[cur].classList.add("on");void bs[cur].offsetWidth;bs[cur].classList.add("on");
    sname.textContent=S[cur].name;
    clearTimeout(timer);timer=setTimeout(()=>show(cur+1),6000);
  };
  dots.addEventListener("click",e=>{const b=e.target.closest("button");if(b)show([...dots.children].indexOf(b))});
  if(!matchMedia("(prefers-reduced-motion: reduce)").matches)show(0);
}
})();
