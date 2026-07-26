from playwright.sync_api import sync_playwright
THEMES=[
 {"key":"editorial","name":"Relay Editorial","domain":"Dev-tool · relay-kit",
  "fonts":"Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600;700",
  "vars":{"--bg":"#FAF6EF","--surface":"#FFFFFF","--surface2":"#F3ECDF","--ink":"#22201C","--muted":"#6E665A","--line":"#E8DFCF","--primary":"#059669","--accent2":"#047857","--onPrimary":"#fff","--radius":"16px","--radiusSm":"9px","--fontD":"Fraunces","--fontS":"Inter","--fontM":"Inter","--ring":"rgba(60,40,25,.14)"},
  "attr":{"data-surface":"border","data-accent":"solid","data-label":"normal"},
  "text":{"appname":"Relay · Control","eyebrow":"Workspace","headline":"Lane control","sub":"Route, run, and prove — one surface.","s1":"skills","s2":"proven","s3":"lanes","cardn":"build-it · search idx","pill":"running","r1":"ready-check","r2":"secure-review","r3":"prove-it"}},

 {"key":"nocturne","name":"Nocturne Ops","domain":"Security · terminal / C2",
  "fonts":"JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600",
  "vars":{"--bg":"#0B0B0C","--surface":"#161617","--surface2":"#1E1E20","--ink":"#E8E6E1","--muted":"#8A8880","--line":"#2A2A2C","--primary":"#A3E635","--accent2":"#EF4444","--onPrimary":"#0B0B0C","--radius":"5px","--radiusSm":"4px","--fontD":"JetBrains Mono","--fontS":"Inter","--fontM":"JetBrains Mono","--ring":"rgba(0,0,0,.6)"},
  "attr":{"data-surface":"flat","data-accent":"solid","data-label":"mono"},
  "text":{"appname":"opsec // console","eyebrow":"engagement","headline":"c2 · fleet","sub":"authorized red-team session · scoped.","s1":"nodes","s2":"uptime","s3":"tasks","cardn":"beacon · worker-01","pill":"live","r1":"recon.sh","r2":"payload.bin","r3":"exfil.log"}},

 {"key":"cobalt","name":"Cobalt Fintech","domain":"Finance · crypto dashboard",
  "fonts":"Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600",
  "vars":{"--bg":"#0A1120","--surface":"#111A2E","--surface2":"#16223A","--ink":"#E6EDF7","--muted":"#7E8DA6","--line":"#1E2C48","--primary":"#22D3EE","--accent2":"#6366F1","--onPrimary":"#04121A","--radius":"12px","--radiusSm":"9px","--fontD":"Space Grotesk","--fontS":"Inter","--fontM":"Space Grotesk","--ring":"rgba(0,0,0,.5)"},
  "attr":{"data-surface":"shadow","data-accent":"gradient","data-label":"normal"},
  "text":{"appname":"Vault","eyebrow":"Portfolio","headline":"Net worth","sub":"Live positions across 6 chains.","s1":"assets","s2":"staked","s3":"alerts","cardn":"ETH · perpetual","pill":"+4.2%","r1":"BTC","r2":"SOL","r3":"USDC"}},

 {"key":"sunset","name":"Sunset Social","domain":"Content · creator / marketing",
  "fonts":"Poppins:wght@400;500;600;700",
  "vars":{"--bg":"#FFF6F2","--surface":"#FFFFFF","--surface2":"#FDEBEF","--ink":"#2C1E29","--muted":"#8A7580","--line":"#F4DDE2","--primary":"#FB5E7E","--accent2":"#A855F7","--onPrimary":"#fff","--radius":"22px","--radiusSm":"16px","--fontD":"Poppins","--fontS":"Poppins","--fontM":"Poppins","--ring":"rgba(180,80,120,.18)"},
  "attr":{"data-surface":"shadow","data-accent":"gradient","data-label":"normal"},
  "text":{"appname":"Studio","eyebrow":"Creator studio","headline":"Good vibes ✦","sub":"3 posts scheduled today.","s1":"posts","s2":"reach","s3":"drafts","cardn":"Reel · launch teaser","pill":"scheduled","r1":"TikTok","r2":"Instagram","r3":"YouTube"}},

 {"key":"slate","name":"Slate Enterprise","domain":"SaaS · operations console",
  "fonts":"Inter:wght@400;500;600;700",
  "vars":{"--bg":"#F7F8FA","--surface":"#FFFFFF","--surface2":"#EEF1F5","--ink":"#1E293B","--muted":"#64748B","--line":"#E2E8F0","--primary":"#4F46E5","--accent2":"#4F46E5","--onPrimary":"#fff","--radius":"10px","--radiusSm":"8px","--fontD":"Inter","--fontS":"Inter","--fontM":"Inter","--ring":"rgba(30,41,59,.1)"},
  "attr":{"data-surface":"border","data-accent":"solid","data-label":"normal"},
  "text":{"appname":"Console","eyebrow":"Operations","headline":"Overview","sub":"Org-wide status at a glance.","s1":"services","s2":"SLA","s3":"tickets","cardn":"Deploy · api-gateway","pill":"in progress","r1":"auth-svc","r2":"billing-svc","r3":"search-svc"}},

 {"key":"commerce","name":"Verdant Commerce","domain":"E-commerce · storefront",
  "fonts":"Sora:wght@500;600;700&family=Inter:wght@400;500;600",
  "vars":{"--bg":"#FFFFFF","--surface":"#FFFFFF","--surface2":"#F4F6F4","--ink":"#14231A","--muted":"#6B7B70","--line":"#E6ECE7","--primary":"#EA580C","--accent2":"#F59E0B","--onPrimary":"#fff","--radius":"14px","--radiusSm":"10px","--fontD":"Sora","--fontS":"Inter","--fontM":"Sora","--ring":"rgba(20,35,26,.1)"},
  "attr":{"data-surface":"shadow","data-accent":"solid","data-label":"normal"},
  "text":{"appname":"Storefront","eyebrow":"Today","headline":"Orders","sub":"32 new orders across 4 channels.","s1":"orders","s2":"fulfilled","s3":"returns","cardn":"Order #10428","pill":"packing","r1":"Shopee","r2":"TikTok Shop","r3":"Lazada"}},
]
with sync_playwright() as p:
    b=p.chromium.launch()
    for t in THEMES:
        pg=b.new_page(viewport={"width":640,"height":600},device_scale_factor=2)
        pg.goto("file:///tmp/themes/app.html",wait_until="networkidle")
        pg.evaluate("""(f)=>{const l=document.createElement('link');l.rel='stylesheet';l.href='https://fonts.googleapis.com/css2?family='+f+'&display=swap';document.head.appendChild(l);}""", t["fonts"])
        css=":root{"+"".join(f"{k}:{v};" for k,v in t["vars"].items())+"}"
        pg.add_style_tag(content=css)
        for k,v in t["attr"].items(): pg.evaluate(f"document.body.setAttribute('{k}','{v}')")
        for eid,val in t["text"].items(): pg.evaluate("([i,v])=>{const e=document.getElementById(i); if(e) e.textContent=v;}",[eid,val])
        pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(1200)
        pg.screenshot(path=f"/tmp/themes/th-{t['key']}.png")
        print("shot",t["name"])
    b.close()
