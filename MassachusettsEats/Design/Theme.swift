import SwiftUI
import UIKit
import CoreText

/// Massachusetts palette, an Atlantic one (provisional, 2026-11-06; Nick decides, playbook/05-naming.md), light only, from
/// state-prompts/MASSACHUSETTS_PROMPT.md's second option (cranberry with Atlantic navy and cream; no team colors or marks): Atlantic navy
/// #13294B (14.4:1 on white) for titles, tint and accents; cranberry #9E1B32 (white on it 7.9:1) for the hand-checked guide cards and
/// honors chips; Cape sand #E2B25A only as a pin and card fill under navy text (7.4:1; as text on white it's 2.0:1); chowder cream
/// #F7F2E6 pages. The names `green`/`gold` are kept from Wisconsin Eats so the shared views read the same; here `green` is Atlantic navy
/// and `gold` is cranberry.
enum Theme {
    static let green = Color(hex: 0x13294B)      // Atlantic navy: titles, tint, primary text accents
    static let green2 = Color(hex: 0x24456F)
    static let gold = Color(hex: 0x9E1B32)       // cranberry: card fills under white text, chips
    static let goldSoft = Color(hex: 0xF3D8DD)   // soft cranberry
    static let lime = Color(hex: 0xE2B25A)       // Cape sand, fills only (hand-checked pins, the title shadow), under navy text
    static let limeSoft = Color(hex: 0xF8EACB)
    static let sand = Color(hex: 0xF7F2E6)       // the Home background, chowder cream
    static let red = Color(hex: 0x9E1B32)        // honors chips
    static let sandstone = Color(hex: 0x7A1426)  // a darker cranberry accent (10.6:1 on white)
    static let teal = Color(hex: 0x1F6577)       // harbor accent (6.6:1 on white)
    static let ink = Color(hex: 0x1A1A1A)
    static let ink2 = Color(hex: 0x2E3440)
    static let muted = Color(hex: 0x5B6270)
    static let surface = Color.white
    static let surface2 = Color(hex: 0xF1EEE6)
    static let surface3 = Color(hex: 0xE4DFD3)
    static let rule = Color(hex: 0xE4DFD3)
    static let rule2 = Color(hex: 0xCCC4B3)
}

extension Color {
    init(hex: UInt32) {
        self.init(red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255)
    }
}

/// A small uppercase label: "STONE CRAB", "1 MICHELIN STAR".
struct Chip: View {
    enum Style { case gold, green, red, plain, dashed }
    let text: String
    var style: Style = .plain

    var body: some View {
        Text(text.uppercased())
            .font(.caption2.weight(.bold))
            .tracking(0.4)
            .padding(.horizontal, 7).padding(.vertical, 3)
            .foregroundStyle(style == .green || style == .red ? Color.white : style == .dashed ? Theme.muted : style == .gold ? Theme.ink : Theme.green)
            .background {
                RoundedRectangle(cornerRadius: 5).fill(style == .gold ? Theme.goldSoft : style == .green ? Theme.green : style == .red ? Theme.red
                                                       : style == .dashed ? .clear : Theme.surface2)
            }
            .overlay {
                if style == .dashed { RoundedRectangle(cornerRadius: 5).strokeBorder(Theme.rule2, style: StrokeStyle(lineWidth: 1, dash: [3, 2])) }
            }
            .accessibilityLabel(text)
    }
}

/// Bay State Eats' lettering: the system face drawn compressed and heavy for titles and guide names (like a show poster), and the
/// system monospaced face for numbers, dates and small labels. No bundled fonts.
struct DisplayFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .black
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight).width(.compressed))
    }
}

/// Numbers, dates and small labels in the system monospaced face, scaled like DisplayFont.
struct MonoFont: ViewModifier {
    let size: CGFloat
    var weight: Font.Weight = .semibold
    @ScaledMetric(relativeTo: .body) private var scale: CGFloat = 1

    func body(content: Content) -> some View {
        content.font(.system(size: size * min(scale, 1.6), weight: weight, design: .monospaced))
    }
}

extension View {
    func displayFont(_ size: CGFloat, weight: Font.Weight = .black) -> some View {
        modifier(DisplayFont(size: size, weight: weight))
    }

    func monoFont(_ size: CGFloat, weight: Font.Weight = .semibold) -> some View {
        modifier(MonoFont(size: size, weight: weight))
    }
}

/// The header band: two Atlantic swells over a cranberry baseline, with the Cape's hook (the "arm" from Buzzards Bay to Provincetown)
/// rising at the right in navy. No flag, seal or arms (a state commission is redesigning them).
struct Stripes: View {
    var height: CGFloat = 6

    /// the Cape, as (x, rise) on the band's right end: the shoulder at the canal, the elbow at Chatham, the hand curling at Provincetown
    static let cape: [(CGFloat, CGFloat)] = [(0.80, 0.0), (0.80, 0.10), (0.90, 0.10), (0.95, 0.20), (0.975, 0.55), (0.965, 0.90),
                                             (0.93, 1.0), (0.885, 0.95), (0.89, 0.80), (0.925, 0.78), (0.935, 0.55), (0.915, 0.36),
                                             (0.87, 0.34), (0.80, 0.40)]

    var body: some View {
        Canvas { ctx, size in
            let w = size.width, h = size.height, base = h * 0.78
            for (i, amp) in [(0.42 as CGFloat), 0.24].enumerated() {
                var p = Path()
                p.move(to: CGPoint(x: 0, y: base))
                let n = 48
                for k in 0...n {
                    let x = CGFloat(k) / CGFloat(n)
                    let y = base - base * (amp * 0.5 * (1 + sin(x * .pi * (i == 0 ? 7 : 11) + CGFloat(i))) + 0.08)
                    p.addLine(to: CGPoint(x: x * w * 0.8, y: y))
                }
                p.addLine(to: CGPoint(x: w * 0.8, y: base)); p.closeSubpath()
                ctx.fill(p, with: .color(Theme.green.opacity([0.45, 1.0][i])))
            }
            var cape = Path()
            cape.move(to: CGPoint(x: Self.cape[0].0 * w, y: base))
            for (x, rise) in Self.cape { cape.addLine(to: CGPoint(x: x * w, y: base - base * rise)) }
            cape.closeSubpath()
            ctx.fill(cape, with: .color(Theme.green))
            // the cranberry baseline last
            ctx.fill(Path(CGRect(x: 0, y: base, width: w, height: h - base)), with: .color(Theme.gold))
        }
        .frame(height: height * 2.4)
        .clipShape(RoundedRectangle(cornerRadius: 3))
        .accessibilityHidden(true)
    }
}

extension View {
    /// An inline navigation title in the display type. UINavigationBar.appearance() didn't reach every SwiftUI bar on iOS 27
    /// (the Map title went from compressed blue to plain black after a push and pop; place titles were always plain), so the
    /// title is our own view in the bar. The navigation title is still set, for the back button and VoiceOver.
    func inlineTitle(_ title: String) -> some View {
        navigationTitle(title)
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .principal) {
                    Text(title).displayFont(19, weight: .heavy).foregroundStyle(Theme.green)
                        .lineLimit(1).minimumScaleFactor(0.7)
                        .accessibilityAddTraits(.isHeader)
                }
            }
    }
}
