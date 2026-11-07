// Bay State Eats icon concepts (2026-11-06), drawn in the shared Eats Ranked style (state-prompts/ICON-STYLE.md): one flat, level,
// centred food on Atlantic navy #13294B (the palette in Design/Theme.swift), no backing shape, no text or texture, no state seal.
// Food hexes: bun #E2B25A (the palette's Cape sand) with its lighter crust #F0CF8E, lobster #D9533B with pale meat #F6D3C2,
// bowl #F7F2E6 (chowder cream) with chowder #E9D7A4 and a cranberry band #9E1B32, sponge #EFC97E, custard #F8E3A0, chocolate #4A2516.
//   A  a cold lobster roll in a split-top bun, side view
//   B  a bowl of clam chowder with oyster crackers, front view
//   C  a Boston cream pie wedge, front view with its chocolate top
// Usage, from ma-eats/: swift scripts/icon-concepts.swift <out dir>   -> concept-{a,b,c}-1024.png
import AppKit
import CoreGraphics
import ImageIO
import UniformTypeIdentifiers

func rgb(_ hex: UInt32) -> CGColor {
    CGColor(srgbRed: CGFloat((hex >> 16) & 255) / 255, green: CGFloat((hex >> 8) & 255) / 255, blue: CGFloat(hex & 255) / 255, alpha: 1)
}
let NAVY: UInt32 = 0x13294B, BUN: UInt32 = 0xE2B25A, CRUST: UInt32 = 0xF0CF8E, LOBSTER: UInt32 = 0xD9533B, MEAT: UInt32 = 0xF6D3C2
let BOWL: UInt32 = 0xF7F2E6, CHOWDER: UInt32 = 0xE9D7A4, CRANBERRY: UInt32 = 0x9E1B32
let SPONGE: UInt32 = 0xEFC97E, CUSTARD: UInt32 = 0xF8E3A0, CHOCOLATE: UInt32 = 0x4A2516

/// A: the lobster roll. CoreGraphics y-up, s = canvas size. Identical to make-brand.swift's lobsterRoll().
func lobsterRoll(_ c: CGContext, _ s: CGFloat) {
    func R(_ x: CGFloat, _ y: CGFloat, _ w: CGFloat, _ h: CGFloat, _ r: CGFloat) -> CGPath {
        CGPath(roundedRect: CGRect(x: x * s, y: y * s, width: w * s, height: h * s), cornerWidth: r * s, cornerHeight: r * s, transform: nil)
    }
    // the lobster salad heaped in the split: three big chunks over a capsule, wider than the bun's top
    c.setFillColor(rgb(LOBSTER))
    c.addPath(R(0.17, 0.47, 0.66, 0.13, 0.065)); c.fillPath()
    for (x, r) in [(0.31, 0.095), (0.50, 0.105), (0.69, 0.095)] as [(CGFloat, CGFloat)] {
        c.fillEllipse(in: CGRect(x: (x - r) * s, y: (0.585 - r) * s, width: 2 * r * s, height: 2 * r * s))
    }
    // pale claw meat in each chunk
    c.setFillColor(rgb(MEAT))
    for (x, y, w) in [(0.25, 0.575, 0.085), (0.455, 0.60, 0.09), (0.665, 0.575, 0.085)] as [(CGFloat, CGFloat, CGFloat)] {
        c.fillEllipse(in: CGRect(x: x * s, y: y * s, width: w * s, height: 0.055 * s))
    }
    // the split-top bun: flat griddled sides, a lighter crust along its top edge
    c.setFillColor(rgb(BUN)); c.addPath(R(0.14, 0.30, 0.72, 0.21, 0.06)); c.fillPath()
    c.setFillColor(rgb(CRUST)); c.addPath(R(0.16, 0.465, 0.68, 0.045, 0.0225)); c.fillPath()
}

/// B: a bowl of chowder, the soup's surface as the lighter top plane, two oyster crackers on it and a cranberry band on the bowl.
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

/// C: a wedge of Boston cream pie: two sponge layers and the custard between them on the front face, the chocolate top as the top
/// plane (apex off-centre, as Wisconsin's wedge), two chocolate drips on the face.
func creamPie(_ c: CGContext, _ s: CGFloat) {
    c.saveGState(); defer { c.restoreGState() }
    c.translateBy(x: 0, y: 0.03 * s)
    c.setFillColor(rgb(SPONGE)); c.fill(CGRect(x: 0.14 * s, y: 0.28 * s, width: 0.72 * s, height: 0.26 * s))
    c.setFillColor(rgb(CUSTARD)); c.fill(CGRect(x: 0.14 * s, y: 0.385 * s, width: 0.72 * s, height: 0.05 * s))
    let top = CGMutablePath()
    top.move(to: CGPoint(x: 0.14 * s, y: 0.54 * s)); top.addLine(to: CGPoint(x: 0.86 * s, y: 0.54 * s))
    top.addLine(to: CGPoint(x: 0.36 * s, y: 0.66 * s)); top.closeSubpath()
    c.setFillColor(rgb(CHOCOLATE)); c.addPath(top); c.fillPath()
    c.fill(CGRect(x: 0.14 * s, y: 0.505 * s, width: 0.72 * s, height: 0.04 * s))
    c.setStrokeColor(rgb(CHOCOLATE)); c.setLineWidth(0.034 * s); c.setLineCap(.round)
    for (x, l) in [(0.30, 0.07), (0.62, 0.05)] as [(CGFloat, CGFloat)] {
        c.move(to: CGPoint(x: x * s, y: 0.52 * s)); c.addLine(to: CGPoint(x: x * s, y: (0.52 - l) * s)); c.strokePath()
    }
}

func render(_ n: Int, _ path: String, _ draw: (CGContext, CGFloat) -> Void) {
    let ctx = CGContext(data: nil, width: n, height: n, bitsPerComponent: 8, bytesPerRow: 0, space: CGColorSpace(name: CGColorSpace.sRGB)!,
                        bitmapInfo: CGImageAlphaInfo.noneSkipLast.rawValue)!
    ctx.setShouldAntialias(true)
    ctx.setFillColor(rgb(NAVY)); ctx.fill(CGRect(x: 0, y: 0, width: n, height: n))
    draw(ctx, CGFloat(n))
    let d = CGImageDestinationCreateWithURL(URL(fileURLWithPath: path) as CFURL, UTType.png.identifier as CFString, 1, nil)!
    CGImageDestinationAddImage(d, ctx.makeImage()!, nil)
    guard CGImageDestinationFinalize(d) else { fatalError("could not write \(path)") }
    print("wrote", path)
}
let out = CommandLine.arguments.count > 1 ? CommandLine.arguments[1] : "playbook/brand"
render(1024, out + "/concept-a-1024.png", lobsterRoll)
render(1024, out + "/concept-b-1024.png", chowder)
render(1024, out + "/concept-c-1024.png", creamPie)
