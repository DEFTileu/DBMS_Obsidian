const SESSION_KEY = "protect_key"

function hexToBytes(hex: string): Uint8Array {
  const arr = new Uint8Array(hex.length / 2)
  for (let i = 0; i < arr.length; i++) {
    arr[i] = parseInt(hex.slice(i * 2, i * 2 + 2), 16)
  }
  return arr
}

async function decryptContent(keyHex: string, encHex: string): Promise<string> {
  const keyBytes = hexToBytes(keyHex)
  const encBytes = hexToBytes(encHex)
  const nonce = encBytes.slice(0, 12)
  const ct = encBytes.slice(12)
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const cryptoKey = await (crypto.subtle as any).importKey("raw", keyBytes, "AES-GCM", false, [
    "decrypt",
  ])
  const plain = await crypto.subtle.decrypt({ name: "AES-GCM", iv: nonce }, cryptoKey, ct)
  return new TextDecoder().decode(plain)
}

function revealContent(article: HTMLElement, key: string, encHex: string) {
  decryptContent(key, encHex).then((html) => {
    article.removeAttribute("data-enc")
    article.classList.remove("protected-gate")
    article.innerHTML = html
  })
}

function setupProtectedPage(article: HTMLElement) {
  const encHex = article.dataset.enc!
  const serverUrl = (document.getElementById("protect-config") as HTMLElement | null)?.dataset
    .server ?? ""

  const cachedKey = sessionStorage.getItem(SESSION_KEY)
  if (cachedKey) {
    revealContent(article, cachedKey, encHex)
    return
  }

  article.innerHTML = `
    <div class="protect-icon">🔒</div>
    <h3>Этот раздел защищён</h3>
    <p>Введите пароль для получения доступа</p>
    <div class="protect-form">
      <input type="password" id="protect-input" placeholder="Пароль..." autocomplete="current-password" />
      <button id="protect-btn" type="button">Войти</button>
      <span class="protect-error" id="protect-error">Неверный пароль</span>
    </div>
  `

  const btn = document.getElementById("protect-btn") as HTMLButtonElement
  const input = document.getElementById("protect-input") as HTMLInputElement
  const errEl = document.getElementById("protect-error") as HTMLElement

  async function unlock() {
    const password = input.value.trim()
    if (!password) return

    btn.disabled = true
    btn.textContent = "Проверка..."
    errEl.style.display = "none"

    try {
      const res = await fetch(`${serverUrl}/cisco/key`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      })

      if (!res.ok) {
        errEl.style.display = "block"
        btn.disabled = false
        btn.textContent = "Войти"
        input.select()
        return
      }

      const { key } = (await res.json()) as { key: string }
      sessionStorage.setItem(SESSION_KEY, key)
      revealContent(article, key, encHex)
    } catch {
      errEl.textContent = "Ошибка подключения к серверу"
      errEl.style.display = "block"
      btn.disabled = false
      btn.textContent = "Войти"
    }
  }

  btn.addEventListener("click", unlock)
  window.addCleanup(() => btn.removeEventListener("click", unlock))

  const keydown = (e: KeyboardEvent) => {
    if (e.key === "Enter") unlock()
  }
  input.addEventListener("keydown", keydown)
  window.addCleanup(() => input.removeEventListener("keydown", keydown))

  input.focus()
}

document.addEventListener("nav", () => {
  const article = document.querySelector<HTMLElement>("article[data-enc]")
  if (article) setupProtectedPage(article)
})
