
function _esc(s){var d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function _addRecent(file,title){
  try{var r=JSON.parse(localStorage.getItem('recentNotes')||'[]');
  r=r.filter(function(x){return x.file!==file;});
  r.unshift({file:file,title:title,t:Date.now()});
  if(r.length>15)r=r.slice(0,15);
  localStorage.setItem('recentNotes',JSON.stringify(r));}catch(e){}
}
function _renderRecent(){
  var el=document.getElementById('recent-list');
  if(!el)return;
  try{var r=JSON.parse(localStorage.getItem('recentNotes')||'[]');
  if(!r.length){el.innerHTML='<span class="empty-hint">暂无记录</span>';return;}
  var h='';r.forEach(function(x){h+='<a href="md.html?file='+encodeURIComponent(x.file)+'">'+_esc(x.title)+'</a>';});
  el.innerHTML=h;}catch(e){el.innerHTML='<span class="empty-hint">暂无记录</span>';}
}
function _toggleFav(file,title){
  try{var f=JSON.parse(localStorage.getItem('favNotes')||'[]');
  var i=f.findIndex(function(x){return x.file===file;});
  if(i>=0)f.splice(i,1);else f.push({file:file,title:title});
  localStorage.setItem('favNotes',JSON.stringify(f));_renderFavs();_updateFavBtn(file);}catch(e){}
}
function _renderFavs(){
  var el=document.getElementById('fav-list');
  if(!el)return;
  try{var f=JSON.parse(localStorage.getItem('favNotes')||'[]');
  if(!f.length){el.innerHTML='<span class="empty-hint">暂无收藏</span>';return;}
  var h='';f.forEach(function(x){h+='<a href="md.html?file='+encodeURIComponent(x.file)+'">'+_esc(x.title)+'</a>';});
  el.innerHTML=h;}catch(e){el.innerHTML='<span class="empty-hint">暂无收藏</span>';}
}
function _updateFavBtn(file){
  var btn=document.getElementById('fav-btn');if(!btn)return;
  try{var f=JSON.parse(localStorage.getItem('favNotes')||'[]');
  var is=f.some(function(x){return x.file===file;});
  btn.textContent=is?'\u2605':'\u2606';btn.classList.toggle('active',is);}catch(e){}
}
(function(){
  var t=localStorage.getItem('theme');
  if(t)document.documentElement.setAttribute('data-theme',t);
})();
document.addEventListener('DOMContentLoaded',function(){
  /* 主题切换 */
  var btn=document.getElementById('theme-toggle');
  if(btn){
    function ui(){btn.textContent=document.documentElement.getAttribute('data-theme')==='dark'?'\u2600':'\u263E';}
    ui();
    btn.addEventListener('click',function(){
      var d=document.documentElement.getAttribute('data-theme')==='dark';
      document.documentElement.setAttribute('data-theme',d?'':'dark');
      localStorage.setItem('theme',d?'':'dark');ui();
    });
  }
  /* 侧边栏开关(移动端) */
  var sb=document.getElementById('sidebar'),ov=document.getElementById('sidebar-overlay');
  function openSb(){if(sb)sb.classList.add('open');if(ov)ov.classList.add('active');document.body.style.overflow='hidden';}
  function closeSb(){if(sb)sb.classList.remove('open');if(ov)ov.classList.remove('active');document.body.style.overflow='';}
  var tg=document.getElementById('sidebar-toggle');
  if(tg)tg.addEventListener('click',openSb);
  var cl=document.getElementById('sidebar-close');
  if(cl)cl.addEventListener('click',closeSb);
  if(ov)ov.addEventListener('click',closeSb);
  /* 文件夹折叠 */
  document.querySelectorAll('.nav-folder').forEach(function(f){
    f.addEventListener('click',function(){this.classList.toggle('collapsed');var c=this.nextElementSibling;if(c&&c.classList.contains('nav-children'))c.classList.toggle('collapsed');});
  });
  /* 高亮当前页 */
  var cp=window.location.pathname.replace(/\/index\.html$/,'').replace(/\/$/,'')||'/';
  document.querySelectorAll('.nav-item').forEach(function(a){
    try{var u=new URL(a.getAttribute('href'),location.href).pathname.replace(/\/index\.html$/,'').replace(/\/$/,'')||'/';
    if(cp===u||location.pathname===a.getAttribute('href'))a.classList.add('active');}catch(e){}
  });
  /* 恢复折叠状态 */
  try{
    var cf=JSON.parse(localStorage.getItem('collapsedFolders')||'[]');
    cf.forEach(function(n){document.querySelectorAll('.nav-folder').forEach(function(f){if(f.dataset.name===n){f.classList.add('collapsed');var c=f.nextElementSibling;if(c)c.classList.add('collapsed');}});});
    document.querySelectorAll('.nav-folder').forEach(function(f){
      f.addEventListener('click',function(){setTimeout(function(){var a=[];document.querySelectorAll('.nav-folder.collapsed').forEach(function(x){if(x.dataset.name)a.push(x.dataset.name);});localStorage.setItem('collapsedFolders',JSON.stringify(a));},60);});
    });
  }catch(e){}
  /* 导览搜索过滤 */
  var searchInput=document.getElementById('nav-search');
  if(searchInput){
    searchInput.addEventListener('input',function(){
      var q=this.value.trim().toLowerCase();
      var items=document.querySelectorAll('.nav-tree .nav-item');
      for(var i=0;i<items.length;i++){
        items[i].style.display=(!q||items[i].textContent.toLowerCase().indexOf(q)!==-1)?'':'none';
      }
      if(q){
        var maxIter=20;
        while(maxIter-->0){
          var changed=false;
          var ch=document.querySelectorAll('.nav-tree .nav-children');
          for(var i=0;i<ch.length;i++){
            var vis=ch[i].querySelectorAll('.nav-item');
            var hasVis=false;
            for(var j=0;j<vis.length;j++){if(vis[j].style.display!=='none'){hasVis=true;break;}}
            if(!hasVis){
              if(ch[i].style.display!=='none'){ch[i].style.display='none';changed=true;}
              var p=ch[i].previousElementSibling;
              if(p&&p.classList.contains('nav-folder')&&p.style.display!=='none'){p.style.display='none';changed=true;}
            }else{
              if(ch[i].style.display==='none'){ch[i].style.display='';changed=true;}
              var p=ch[i].previousElementSibling;
              if(p&&p.classList.contains('nav-folder')&&p.style.display==='none'){p.style.display='';changed=true;}
            }
          }
          if(!changed)break;
        }
      }else{
        var allFolders=document.querySelectorAll('.nav-tree .nav-children, .nav-tree .nav-folder');
        for(var i=0;i<allFolders.length;i++) allFolders[i].style.display='';
      }
    });
  }
  /* md.html 高亮当前文件 */
  try{
    var fp=new URLSearchParams(location.search).get('file');
    if(fp){
      document.querySelectorAll('.nav-item').forEach(function(a){
        try{var u=new URL(a.href);if(u.searchParams.get('file')===fp)a.classList.add('active');}catch(e){}
      });
    }
  }catch(e){}
  /* 渲染最近浏览 & 收藏 */
  _renderRecent();
  _renderFavs();
  /* 键盘快捷键 */
  document.addEventListener('keydown',function(e){
    var tag=document.activeElement.tagName;
    if((e.ctrlKey||e.metaKey)&&!e.shiftKey&&e.key==='k'){
      e.preventDefault();
      var s=document.getElementById('nav-search');
      if(s){s.focus();s.select();}
    }
    if((e.ctrlKey||e.metaKey)&&e.shiftKey&&e.key==='K'){
      e.preventDefault();
      if(window._openGlobalSearch)window._openGlobalSearch();
    }
    if(e.key==='t'&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&tag!=='INPUT'&&tag!=='TEXTAREA'){
      if(btn)btn.click();
    }
    if(e.key==='?'&&!e.ctrlKey&&!e.metaKey&&!e.altKey&&tag!=='INPUT'&&tag!=='TEXTAREA'){
      e.preventDefault();
      var o=document.getElementById('shortcut-overlay');
      if(o)o.classList.toggle('active');
    }
    if(e.key==='Escape'){
      var o=document.getElementById('shortcut-overlay');
      if(o)o.classList.remove('active');
    }
  });
  var so=document.getElementById('shortcut-overlay');
  if(so)so.addEventListener('click',function(e){if(e.target===this)this.classList.remove('active');});
  /* 返回顶部 */
  var btt=document.getElementById('back-to-top');
  if(btt){
    window.addEventListener('scroll',function(){btt.classList.toggle('visible',window.scrollY>400);},{passive:true});
    btt.addEventListener('click',function(){window.scrollTo({top:0,behavior:'smooth'});});
  }
  /* 全局搜索 */
  var gsOverlay=document.getElementById('global-search-overlay');
  var gsInput=document.getElementById('global-search-input');
  var gsResults=document.getElementById('global-search-results');
  if(gsOverlay&&gsInput&&gsResults){
    var gsIdx=-1,gsItems=[];
    function gsOpen(){gsOverlay.classList.add('active');gsInput.value='';gsResults.innerHTML='';gsIdx=-1;gsItems=[];setTimeout(function(){gsInput.focus();},50);}
    function gsClose(){gsOverlay.classList.remove('active');}
    gsInput.addEventListener('input',function(){
      var q=this.value.trim().toLowerCase();
      if(!q){gsResults.innerHTML='<div class="global-search-empty">输入关键词搜索所有笔记</div>';gsItems=[];gsIdx=-1;return;}
      var navItems=document.querySelectorAll('.nav-tree .nav-item');
      var results=[];
      navItems.forEach(function(a){
        var href=a.getAttribute('href');
        if(!href||!href.indexOf('file='))return;
        var fMatch=a.textContent.toLowerCase().indexOf(q)!==-1;
        results.push({title:a.textContent,href:href,score:fMatch?1:2,file:decodeURIComponent(href.split('file=')[1])});
      });
      results.sort(function(a,b){return a.score-b.score||a.title.localeCompare(b.title);});
      results=results.slice(0,20);
      if(!results.length){gsResults.innerHTML='<div class="global-search-empty">未找到匹配笔记</div>';gsItems=[];gsIdx=-1;return;}
      /* 去重 */
      var seen={};results=results.filter(function(r){if(seen[r.file])return false;seen[r.file]=true;return true;});
      gsItems=[];
      var h='';
      results.forEach(function(r,i){
        h+='<div class="global-search-item" data-idx="'+i+'" data-href="'+r.href+'">'
          +'<span class="gsearch-icon">&#128196;</span>'
          +'<div class="gsearch-text"><div class="gsearch-title">'+_esc(r.title)+'</div>'
          +'<div class="gsearch-path">'+_esc(r.file)+'</div></div></div>';
        gsItems.push(r);
      });
      gsResults.innerHTML=h;gsIdx=-1;
      gsResults.querySelectorAll('.global-search-item').forEach(function(el){
        el.addEventListener('click',function(){window.location.href=this.dataset.href;});
        el.addEventListener('mouseenter',function(){gsFocus(+this.dataset.idx);});
      });
      gsFocus(0);
    });
    gsInput.addEventListener('keydown',function(e){
      if(e.key==='Escape')gsClose();
      if(e.key==='Enter'&&gsIdx>=0&&gsItems[gsIdx])window.location.href=gsItems[gsIdx].href;
      if(e.key==='ArrowDown'){e.preventDefault();gsFocus(gsIdx+1);}
      if(e.key==='ArrowUp'){e.preventDefault();gsFocus(gsIdx-1);}
    });
    gsOverlay.addEventListener('click',function(e){if(e.target===gsOverlay)gsClose();});
    function gsFocus(idx){
      if(!gsItems.length)return;
      idx=((idx%gsItems.length)+gsItems.length)%gsItems.length;
      gsIdx=idx;
      gsResults.querySelectorAll('.global-search-item').forEach(function(el,i){
        el.classList.toggle('focused',i===idx);
        if(i===idx)el.scrollIntoView({block:'nearest'});
      });
    }
    window._openGlobalSearch=gsOpen;
  }
});

// ═══ 电子桌宠 ═══
document.addEventListener('DOMContentLoaded',function(){
  var PX=4,G=8,SZ=PX*G;
  var st={skin:'cat',mood:80,hunger:70,acc:null,x:null};
  try{var s=JSON.parse(localStorage.getItem('petState'));if(s){for(var k in s)if(s[k]!=null)st[k]=s[k];}}catch(e){}
  var P={
    cat:{b:'#FFB347',p:'#FF9999',e:'#2d2d2d',n:'#FF6B6B',w:'#eee'},
    dog:{b:'#C49A6C',p:'#8B6914',e:'#2d2d2d',n:'#FF6B6B',w:'#eee'},
    rabbit:{b:'#F0EDE5',p:'#FFB6C1',e:'#2d2d2d',n:'#FF6B6B',w:'#ddd'}
  };
  var FR={
    cat:{
      idle:[[0,'p',0,0,0,0,'p',0],[0,'b',0,0,0,0,'b',0],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]],
      walk:[[0,'p',0,0,0,0,'p',0],[0,'b',0,0,0,0,'b',0],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],['b',0,'b',0,0,'b',0,'b']],
      sleep:[[0,'p',0,0,0,0,'p',0],[0,'b',0,0,0,0,'b',0],[0,'b','b','b','b','b','b',0],[0,'b','w',0,0,'w','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]],
      eat:[[0,'p',0,0,0,0,'p',0],[0,'b',0,0,0,0,'b',0],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','n','n','n','b','b',0],[0,'b','b','b','b','b','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]]
    },
    dog:{
      idle:[['p',0,0,0,0,0,0,'p'],['p','b',0,0,0,0,'b','p'],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]],
      walk:[['p',0,0,0,0,0,0,'p'],['p','b',0,0,0,0,'b','p'],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],['b',0,'b',0,0,'b',0,'b']],
      sleep:[['p',0,0,0,0,0,0,'p'],['p','b',0,0,0,0,'b','p'],[0,'b','b','b','b','b','b',0],[0,'b','w',0,0,'w','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]],
      eat:[['p',0,0,0,0,0,0,'p'],['p','b',0,0,0,0,'b','p'],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','n','n','n','b','b',0],[0,'b','b','b','b','b','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]]
    },
    rabbit:{
      idle:[[0,0,'p',0,0,'p',0,0],[0,0,'b',0,0,'b',0,0],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]],
      walk:[[0,0,'p',0,0,'p',0,0],[0,0,'b',0,0,'b',0,0],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],['b',0,'b',0,0,'b',0,'b']],
      sleep:[[0,0,'p',0,0,'p',0,0],[0,0,'b',0,0,'b',0,0],[0,'b','b','b','b','b','b',0],[0,'b','w',0,0,'w','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b','n','b',0,0,0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]],
      eat:[[0,0,'p',0,0,'p',0,0],[0,0,'b',0,0,'b',0,0],[0,'b','b','b','b','b','b',0],[0,'b','e',0,0,'e','b',0],[0,'b','n','n','n','b','b',0],[0,'b','b','b','b','b','b',0],[0,'b','b','b','b','b','b',0],[0,0,'b',0,0,'b',0,0]]
    }
  };
  function mkSh(fr,pal){var s=[];for(var r=0;r<fr.length;r++)for(var c=0;c<fr[r].length;c++)if(fr[r][c]&&pal[fr[r][c]])s.push((c*PX)+'px '+(r*PX)+'px 0 '+pal[fr[r][c]]);return s.join(',');}
  function save(){try{localStorage.setItem('petState',JSON.stringify(st));}catch(e){}}
  var wrap=document.createElement('div');wrap.className='pet-wrap';
  if(st.x!=null)wrap.style.left=st.x+'px';
  var bubble=document.createElement('div');bubble.className='pet-bubble';
  var moodBar=document.createElement('div');moodBar.className='pet-mood-bar';
  var moodFill=document.createElement('div');moodFill.className='pet-mood-fill';moodBar.appendChild(moodFill);
  var accHat=document.createElement('div');accHat.className='pet-acc pet-acc-hat';
  var accBow=document.createElement('div');accBow.className='pet-acc pet-acc-bow';
  var sprite=document.createElement('div');sprite.className='pet-sprite float';
  var btns=document.createElement('div');btns.className='pet-btns';
  var feedBtn=document.createElement('div');feedBtn.className='pet-btn';feedBtn.textContent='\uD83C\uDF56';feedBtn.title='\u5582\u98DF';
  var menuBtn=document.createElement('div');menuBtn.className='pet-btn';menuBtn.textContent='\u2728';menuBtn.title='\u6362\u88C5';
  btns.appendChild(feedBtn);btns.appendChild(menuBtn);
  var menu=document.createElement('div');menu.className='pet-menu';
  wrap.appendChild(bubble);wrap.appendChild(moodBar);wrap.appendChild(accHat);wrap.appendChild(accBow);
  wrap.appendChild(sprite);wrap.appendChild(btns);wrap.appendChild(menu);
  document.body.appendChild(wrap);
  var curSt='idle',walkDir=1,frameTick=0;
  function render(){
    var sk=FR[st.skin];if(!sk)return;
    var fr=sk[curSt]||sk.idle;
    sprite.style.boxShadow=mkSh(fr,P[st.skin]);
    sprite.style.transform=walkDir===-1?'scaleX(-1)':'';
    if(curSt==='sleep'){sprite.classList.remove('float');sprite.style.animation='petBreathe 2.5s ease-in-out infinite';}
    else if(curSt==='idle'){sprite.style.animation='';void sprite.offsetWidth;sprite.classList.add('float');}
    else{sprite.classList.remove('float');sprite.style.animation='';}
    accHat.classList.toggle('show',st.acc==='hat');accBow.classList.toggle('show',st.acc==='bow');
    var avg=(st.mood+st.hunger)/2;
    moodFill.style.width=Math.max(0,Math.min(100,avg))+'%';
    moodFill.style.background=avg>60?'#4CAF50':avg>30?'#FF9800':'#f44336';
  }
  render();
  var bTimer=null;
  function showBub(txt,dur){bubble.textContent=txt;bubble.classList.add('show');clearTimeout(bTimer);bTimer=setTimeout(function(){bubble.classList.remove('show');},dur||2500);}
  var clickT=['\u55B5~','\u4F60\u597D\u5440\uFF01','\u6478\u6478\u6211~','\u4ECA\u5929\u771F\u597D','\u563B\u563B','\u522B\u6320\u6211~','(=\u00B7\u03C9\u00B7=)','\u6E9C\u4E86\u6E9C~','\u4E3B\u4EBA\u6765\u5566\uFF01'];
  var hungT=['\u809A\u5B50\u997F\u4E86...','\u60F3\u5403\u5C0F\u9C7C\u5E72','\u597D\u997F\u5440','\u6709\u5403\u7684\u5417','\u5495\u565C\u5495\u565C~'];
  var sadT=['\u4E3B\u4EBA\u4E0D\u7406\u6211...','\u597D\u65E0\u804A\u554A','\u966A\u6211\u73A9\u561B','\u54FC\uFF01','\u4E00\u4E2A\u4EBA\u597D\u51B7\u6E05'];
  var slpT=['\u597D\u56F0...','Zzz...','\u547C\u565C\u547C\u565C~','\u8BA9\u6211\u518D\u7761\u4F1A\u513F'];
  function rnd(a){return a[Math.floor(Math.random()*a.length)];}
  var clickLock=false;
  wrap.addEventListener('click',function(e){
    if(e.target.closest('.pet-btn')||e.target.closest('.pet-menu'))return;
    if(clickLock||wasDrag)return;
    st.mood=Math.min(100,st.mood+5);save();
    if(curSt==='sleep'){curSt='idle';showBub('\u554A\uFF01\u9192\u5566~',1500);render();setTimeout(startAI,1500);return;}
    var txt=st.hunger<30?rnd(hungT):st.mood<30?rnd(sadT):rnd(clickT);
    showBub(txt);clickLock=true;
    sprite.classList.remove('float');sprite.style.animation='petJump 0.35s ease';
    setTimeout(function(){sprite.style.animation='';if(curSt==='idle')sprite.classList.add('float');clickLock=false;},350);
    render();
  });
  feedBtn.addEventListener('click',function(e){
    e.stopPropagation();
    if(st.hunger>=100){showBub('\u5DF2\u7ECF\u5403\u9971\u5566~');return;}
    st.hunger=Math.min(100,st.hunger+30);st.mood=Math.min(100,st.mood+3);save();
    showBub('\u597D\u5403\uFF01',1500);
    var prev=curSt;curSt='eat';render();
    sprite.style.animation='petEat 0.4s ease';
    setTimeout(function(){curSt=prev;sprite.style.animation='';render();},400);
  });
  function buildMenu(){
    var h='<div class="pet-menu-label">\u89D2\u8272</div>';
    var sn={cat:'\u5C0F\u732B',dog:'\u5C0F\u72D7',rabbit:'\u5C0F\u5154'};
    var sc={cat:'#FFB347',dog:'#C49A6C',rabbit:'#F0EDE5'};
    for(var k in sn)h+='<div class="pet-menu-item'+(st.skin===k?' active':'')+'" data-skin="'+k+'"><span class="pmi-dot" style="background:'+sc[k]+'"></span>'+sn[k]+'</div>';
    h+='<div class="pet-menu-label" style="margin-top:6px">\u88C5\u9970</div>';
    var an={hat:'\u5E3D\u5B50',bow:'\u8774\u8776\u7ED3'};var ad={hat:'#E74C3C',bow:'#FF69B4};
    h+='<div class="pet-menu-item'+(st.acc===null?' active':'')+'" data-acc="none"><span class="pmi-dot" style="background:var(--muted);opacity:0.3"></span>\u65E0</div>';
    for(var a in an)h+='<div class="pet-menu-item'+(st.acc===a?' active':'')+'" data-acc="'+a+'"><span class="pmi-dot" style="background:'+ad[a]+'"></span>'+an[a]+'</div>';
    menu.innerHTML=h;
    menu.querySelectorAll('[data-skin]').forEach(function(el){el.addEventListener('click',function(e){e.stopPropagation();st.skin=this.dataset.skin;save();buildMenu();render();});});
    menu.querySelectorAll('[data-acc]').forEach(function(el){el.addEventListener('click',function(e){e.stopPropagation();st.acc=this.dataset.acc==='none'?null:this.dataset.acc;save();buildMenu();render();});});
  }
  menuBtn.addEventListener('click',function(e){e.stopPropagation();menu.classList.toggle('show');if(menu.classList.contains('show'))buildMenu();});
  document.addEventListener('click',function(e){if(!e.target.closest('.pet-menu')&&!e.target.closest('.pet-btn'))menu.classList.remove('show');});
  var dragging=false,wasDrag=false,dragOX=0,dragOY=0;
  function dragStart(e){
    if(e.target.closest('.pet-btn')||e.target.closest('.pet-menu'))return;
    if(aiWalking)return;dragging=true;wasDrag=false;
    var rect=wrap.getBoundingClientRect();
    var cx=e.touches?e.touches[0].clientX:e.clientX;var cy=e.touches?e.touches[0].clientY:e.clientY;
    dragOX=cx-rect.left;dragOY=cy-rect.top;wrap.classList.add('dragging');
    sprite.classList.remove('float');sprite.style.animation='';e.preventDefault();
  }
  function dragMove(e){
    if(!dragging)return;wasDrag=true;
    var cx=e.touches?e.touches[0].clientX:e.clientX;var cy=e.touches?e.touches[0].clientY:e.clientY;
    var x=cx-dragOX,y=window.innerHeight-cy-dragOY-SZ;
    var minL=window.innerWidth>768?280:10;
    x=Math.max(minL,Math.min(window.innerWidth-SZ-40,x));
    y=Math.max(10,Math.min(window.innerHeight-SZ-40,y));
    wrap.style.left=x+'px';wrap.style.bottom=y+'px';st.x=x;e.preventDefault();
  }
  function dragEnd(){if(!dragging)return;dragging=false;wrap.classList.remove('dragging');save();if(curSt==='idle')sprite.classList.add('float');}
  wrap.addEventListener('mousedown',dragStart);wrap.addEventListener('touchstart',dragStart,{passive:false});
  document.addEventListener('mousemove',dragMove);document.addEventListener('touchmove',dragMove,{passive:false});
  document.addEventListener('mouseup',dragEnd);document.addEventListener('touchend',dragEnd);
  var aiTimer=null,aiWalking=false,aiWalkAF=null;
  function startAI(){
    clearInterval(aiTimer);if(aiWalkAF)cancelAnimationFrame(aiWalkAF);aiWalking=false;
    aiTimer=setInterval(function(){
      st.hunger=Math.max(0,st.hunger-2);st.mood=Math.max(0,st.mood-1);
      if(st.hunger<20&&Math.random()<0.3)showBub(rnd(hungT));
      else if(st.mood<20&&Math.random()<0.2)showBub(rnd(sadT));
      save();render();
    },60000);
    schedAI();
  }
  function schedAI(){
    if(curSt==='sleep'){setTimeout(function(){curSt='idle';render();schedAI();},8000+Math.random()*12000);return;}
    setTimeout(function(){
      if(aiWalking)return schedAI();
      var r=Math.random();
      if(r<0.55){
        aiWalking=true;curSt='walk';walkDir=Math.random()<0.5?1:-1;render();
        var sx=parseInt(wrap.style.left)||276;
        var tx=walkDir===1?sx+60+Math.random()*140:sx-60-Math.random()*140;
        tx=Math.max(280,Math.min(window.innerWidth-SZ-50,tx));
        var dur=2000+Math.random()*2000,t0=Date.now();
        function step(){
          if(!aiWalking){curSt='idle';render();schedAI();return;}
          var t=Math.min(1,(Date.now()-t0)/dur);
          var ease=t<0.5?2*t*t:-1+(4-2*t)*t;
          var x=sx+(tx-sx)*ease;wrap.style.left=x+'px';st.x=x;
          frameTick=(frameTick+1)%2;
          var sk=FR[st.skin];sprite.style.boxShadow=mkSh(frameTick?sk.walk:sk.idle,P[st.skin]);
          if(t>=1){aiWalking=false;curSt='idle';render();save();schedAI();}
          else aiWalkAF=requestAnimationFrame(step);
        }
        aiWalkAF=requestAnimationFrame(step);
      }else if(r<0.75){curSt='idle';render();schedAI();}
      else if(r<0.9){curSt='sleep';showBub(rnd(slpT),3000);render();schedAI();}
      else{showBub(st.hunger<30?rnd(hungT):st.mood<30?rnd(sadT):rnd(clickT));schedAI();}
    },3000+Math.random()*5000);
  }
  startAI();
  window.addEventListener('beforeunload',save);
});
