from selenium.webdriver.common.by import By

def accept_cookies_if_present(driver, timeout=6):
    accept_selectors = [
        "button.accept-cookies",
        "button#acceptCookies",
        ".cookie-consent button",
        ".cc-accept",
        "button.cookie-accept",
        "button.cookie-btn",
        ".cookie-banner .btn",
        "button[aria-label*='accept']",
        "button[aria-label*='Aceitar']",
        "button[title*='Aceitar']"
    ]

    texts_to_match = ["aceitar", "aceito", "concordo", "permissão", "permitir",
                      "accept", "agree", "ok", "ok, entendi", "fechar"]

    def try_click(el):
        try:
            el.click()
            return True
        except Exception:
            try:
                driver.execute_script("arguments[0].click();", el)
                return True
            except Exception:
                return False

 
    for sel in accept_selectors:
        try:
            elems = driver.find_elements(By.CSS_SELECTOR, sel)
        except Exception:
            elems = []
        if elems:
            for e in elems:
                if try_click(e):
                    return True

   
    try:
        btns = driver.find_elements(By.TAG_NAME, "button")
        for b in btns:
            try:
                txt = (b.text or "").strip().lower()
            except Exception:
                txt = ""
            for t in texts_to_match:
                if t in txt:
                    if try_click(b):
                        return True
    except Exception:
        pass

    
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for frame in iframes:
            try:
                driver.switch_to.frame(frame)
                
                for sel in accept_selectors:
                    try:
                        elems = driver.find_elements(By.CSS_SELECTOR, sel)
                    except Exception:
                        elems = []
                    if elems:
                        for e in elems:
                            if try_click(e):
                                driver.switch_to.default_content()
                                return True
                
                try:
                    btns = driver.find_elements(By.TAG_NAME, "button")
                    for b in btns:
                        try:
                            txt = (b.text or "").strip().lower()
                        except Exception:
                            txt = ""
                        for t in texts_to_match:
                            if t in txt:
                                if try_click(b):
                                    driver.switch_to.default_content()
                                    return True
                except Exception:
                    pass
            except Exception:
                
                pass
            finally:
                try:
                    driver.switch_to.default_content()
                except Exception:
                    pass
    except Exception:
        pass

    
    try:
        
        js_remove_candidates = [
            "document.querySelector('.cookie-consent')",
            "document.querySelector('.cookie-banner')",
            "document.querySelector('.cc-window')",
            "document.querySelector('.cookie')"
        ]
        for js_sel in js_remove_candidates:
            try:
                script = f"var el = {js_sel}; if(el) el.parentNode.removeChild(el);"
                driver.execute_script(script)
            except Exception:
                pass

        
        cleanup_script = """
        var nodes = document.querySelectorAll('body *');
        for(var i=0;i<nodes.length;i++){
            try{
                var s = window.getComputedStyle(nodes[i]);
                if(s.position && (s.position==='fixed' || s.position==='sticky')){
                    var h = nodes[i].getBoundingClientRect().height;
                    var w = nodes[i].getBoundingClientRect().width;
                    var z = parseInt(s.zIndex)||0;
                    if((h>30 || w>100) && z>0){
                        nodes[i].parentNode.removeChild(nodes[i]);
                    }
                }
            }catch(e){}
        }
        """
        driver.execute_script(cleanup_script)
        return True
    except Exception:
        pass

    return False