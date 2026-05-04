// @ts-ignore
import protectScript from "./scripts/protect.inline"
import protectStyle from "./styles/protect.scss"
import { QuartzComponent, QuartzComponentConstructor, QuartzComponentProps } from "./types"

interface Options {
  serverUrl: string
}

export default ((opts: Options) => {
  const ProtectedGate: QuartzComponent = (_props: QuartzComponentProps) => {
    return <span id="protect-config" data-server={opts.serverUrl} style="display:none" />
  }

  ProtectedGate.afterDOMLoaded = protectScript
  ProtectedGate.css = protectStyle
  return ProtectedGate
}) satisfies QuartzComponentConstructor<Options>
