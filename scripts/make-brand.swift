// Bay State Eats brand (provisional, 2026-11-06; Nick picks the name, icon and palette): the app icon is concept B of
// scripts/icon-concepts.swift, a bowl of clam chowder with oyster crackers, on Atlantic navy; the shared Eats Ranked icon style,
// state-prompts/ICON-STYLE.md, no backing shape. No state flag, seal or arms (a commission is redesigning them), no team marks.
// Usage, from ma-eats/: swift scripts/make-brand.swift   -> MassachusettsEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png,
// docs/ favicons and touch icons, docs/og.png. scripts/make-site.py draws the same mark as its inline SVG: change both together.
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let NAVY: UInt32 = 0x13294B, BUN: UInt32 = 0xE2B25A, BOWL: UInt32 = 0xF7F2E6, CHOWDER: UInt32 = 0xE9D7A4, CRANBERRY: UInt32 = 0x9E1B32
let CREAM: UInt32 = 0xF7F2E6

/// The chowder bowl (concept B of icon-concepts.swift; keep the two identical): a bowl of chowder, the soup's surface as the lighter top plane, two oyster crackers on it and a cranberry band on the bowl.
func chowder(_ c: CGContext, _ s: CGFloat) {
    c.saveGState(); defer { c.restoreGState() }
    c.translateBy(x: 0, y: 0.05 * s)   // the mass a little low, as the references sit
    let bowl = CGMutablePath()
    bowl.move(to: CGPoint(x: 0.15 * s, y: 0.535 * s))
    bowl.addCurve(to: CGPoint(x: 0.38 * s, y: 0.25 * s), control1: CGPoint(x: 0.15 * s, y: 0.36 * s), control2: CGPoint(x: 0.25 * s, y: 0.25 * s))
    bowl.addLine(to: CGPoint(x: 0.62 * s, y: 0.25 * s))
    bowl.addCurve(to: CGPoint(x: 0.85 * s, y: 0.535 * s), control1: CGPoint(x: 0.75 * s, y: 0.25 * s), control2: CGPoint(x: 0.85 * s, y: 0.36 * s))
    bowl.closeSubpath()
    c.setFillColor(rgb(BOWL)); c.addPath(bowl); c.fillPath()
    c.saveGState(); c.addPath(bowl); c.clip()
    c.setFillColor(rgb(CRANBERRY)); c.fill(CGRect(x: 0, y: 0.38 * s, width: s, height: 0.045 * s))
    c.restoreGState()
    c.setFillColor(rgb(CHOWDER)); c.fillEllipse(in: CGRect(x: 0.15 * s, y: 0.48 * s, width: 0.70 * s, height: 0.11 * s))
    c.setFillColor(rgb(BUN))
    for (x, y) in [(0.36, 0.535), (0.55, 0.545)] as [(CGFloat, CGFloat)] {
        c.fillEllipse(in: CGRect(x: x * s, y: y * s, width: 0.10 * s, height: 0.075 * s))
    }
}


func render(_ n: Int, _ path: String, background: Bool) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: background ? CGImageAlphaInfo.noneSkipLast.rawValue : CGImageAlphaInfo.premultipliedLast.rawValue)!
    ctx.setShouldAntialias(true)
    if background { ctx.setFillColor(rgb(NAVY)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n)) }
    chowder(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
render(1024, "MassachusettsEats/Resources/Assets.xcassets/AppIcon.appiconset/icon-1024.png", background: true)
try? FileManager.default.createDirectory(atPath: "docs", withIntermediateDirectories: true)
for (n, name) in [(512, "icon-512.png"), (192, "icon-192.png"), (180, "apple-touch-icon.png"), (32, "favicon-32.png")] {
    render(n, "docs/" + name, background: true)
}

/// The share image (1200 x 630): navy, the bowl at the left, the name and tagline at the right, and the app's header band along the
/// bottom: two Atlantic swells and the Cape's hook over a cranberry baseline, on cream (Theme.swift's Stripes).
func og(_ path: String) {
    let W = 1200, H = 630
    let ctx = CGContext(data: nil, width: W, height: H, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(NAVY)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: H))
    let band: CGFloat = 70, base: CGFloat = 14, w = CGFloat(W) * 0.8
    ctx.setFillColor(rgb(CREAM)); ctx.fill(CGRect(x: 0, y: 0, width: W, height: Int(band)))
    for (i, amp) in [(0.42 as CGFloat), 0.24].enumerated() {
        let p = CGMutablePath(); p.move(to: CGPoint(x: 0, y: base))
        for k in 0...48 {
            let x = CGFloat(k) / 48
            p.addLine(to: CGPoint(x: x * w, y: base + (band - base) * (amp * 0.5 * (1 + sin(x * .pi * (i == 0 ? 7 : 11) + CGFloat(i))) + 0.08)))
        }
        p.addLine(to: CGPoint(x: w, y: base)); p.closeSubpath()
        ctx.setFillColor(rgb(NAVY).copy(alpha: [0.45, 1.0][i])!); ctx.addPath(p); ctx.fillPath()
    }
    let cape: [(CGFloat, CGFloat)] = [(0.80, 0.0), (0.80, 0.10), (0.90, 0.10), (0.95, 0.20), (0.975, 0.55), (0.965, 0.90), (0.93, 1.0),
                                      (0.885, 0.95), (0.89, 0.80), (0.925, 0.78), (0.935, 0.55), (0.915, 0.36), (0.87, 0.34), (0.80, 0.40)]
    let cp = CGMutablePath(); cp.move(to: CGPoint(x: 0.80 * CGFloat(W), y: base))
    for (x, r) in cape { cp.addLine(to: CGPoint(x: x * CGFloat(W), y: base + (band - base) * r)) }
    cp.closeSubpath(); ctx.setFillColor(rgb(NAVY)); ctx.addPath(cp); ctx.fillPath()
    ctx.setFillColor(rgb(CRANBERRY)); ctx.fill(CGRect(x: 0, y: 0, width: CGFloat(W), height: base))
    ctx.saveGState(); ctx.translateBy(x: 40, y: 90); chowder(ctx, 500); ctx.restoreGState()
    let ns = NSGraphicsContext(cgContext: ctx, flipped: false)
    NSGraphicsContext.saveGraphicsState(); NSGraphicsContext.current = ns
    let title = NSFont(name: "AvenirNextCondensed-Heavy", size: 80) ?? NSFont.boldSystemFont(ofSize: 70)
    let sub = NSFont(name: "AvenirNextCondensed-DemiBold", size: 34) ?? NSFont.boldSystemFont(ofSize: 30)
    NSAttributedString(string: "BAY STATE", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 560, y: 380))
    NSAttributedString(string: "EATS", attributes: [.font: title, .foregroundColor: NSColor.white]).draw(at: NSPoint(x: 560, y: 296))
    NSAttributedString(string: "CLAM SHACKS, ROAST BEEF & DIM SUM", attributes: [.font: sub, .foregroundColor: NSColor(srgbRed: 0.886, green: 0.698, blue: 0.353, alpha: 1)]).draw(at: NSPoint(x: 564, y: 246))
    NSGraphicsContext.restoreGraphicsState()
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
og("docs/og.png")
