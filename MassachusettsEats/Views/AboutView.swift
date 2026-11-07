import SwiftUI

struct AboutView: View {
    @Environment(AppModel.self) private var model

    var body: some View {
        List {
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Text("BAY STATE EATS").displayFont(32).foregroundStyle(Theme.green)
                    Text("A free guide to \(model.restaurantCount.formatted()) Massachusetts restaurants, with MICHELIN and James Beard honors and hand-checked lists of Massachusetts's own food: North Shore roast beef, clam shacks and lobster rolls, the North End, Portuguese kitchens, classic diners, Chinatown dim sum and bakeries, and historic taverns and inns. No account, no ads, no tracking.")
                        .font(.subheadline).foregroundStyle(Theme.ink2)
                    Text("Bay State Eats is an independent app by Nicholas Soderstrom. It is not affiliated with, endorsed by or operated by the Commonwealth of Massachusetts, the Department of Public Health, any city or town or its board of health or licensing board (including Boston, Cambridge and Somerville), the Massachusetts Office of Travel and Tourism or any visitor bureau, Michelin, the James Beard Foundation, Apple, or any restaurant or chain. Other names are trademarks of their owners.")
                        .font(.footnote).foregroundStyle(Theme.muted)
                }
                .padding(.vertical, 4)
            }
            Section("How the lists are built") {
                Text("Hand-checked lists (North Shore roast beef, clam shacks and lobster rolls, the North End, Portuguese, classic diners, Chinatown dim sum and bakeries, historic taverns and inns, and the oldest places) include only places checked against a 2025 or 2026 source (a dated magazine or news story, or a visitor bureau's own guide or listing), with the address checked. Founding years mean the year it opened at this address.")
                Text("Honors are MICHELIN Guide Boston's selection (Greater Boston only: one star, Bib Gourmands and recommended restaurants) and James Beard Foundation winners, finalists, semifinalists and America's Classics.")
                Text("Massachusetts publishes no statewide open list of its restaurants. This app starts from open map listings (Overture Maps), adds Cambridge's and Somerville's permitted restaurants, and keeps the kinds of listing those two cities' lists confirmed most often: high-confidence listings matched an official record about nine times in ten. Each place is filed under its city or town, with its neighborhood or village alongside. Whether a place serves alcohol is known only from Somerville's licenses; elsewhere it's unknown, never no. Adult clubs are left out, and stadium, airport and campus stands are hidden with the non-restaurants. Website links are checked, and any that no longer belong to the place are left out.")
                Text("Each city and town's board of health inspects its restaurants, and there's no statewide record or grade. Cambridge publishes its inspections as open data, so its places show the latest one in the city's own terms (no violations, or the codes cited), dated; this app computes no grade. Boston places link to the city's own inspection search.")
                Text("Ratings, reviews, hours and photos are Apple Maps' own, shown live in Apple's place card. This app doesn't store or rank by them.")
            }
            .font(.subheadline).foregroundStyle(Theme.ink2)
            Section("Sources") {
                source("City of Cambridge", "Food establishment permits and sanitary inspections (Inspectional Services Department), from Cambridge's open data portal, under the Open Data Commons Public Domain Dedication and License.", Links.cambridgeInspections.absoluteString)
                source("City of Somerville", "Food establishment permits, common victualler licenses and restaurant licenses with alcohol (SomerStat), from Somerville's open data portal, under the Open Data Commons Open Database License.", "https://data.somervillema.gov/d/nneb-s3f7")
                source("City of Boston", "Inspectional Services' own inspection search, linked from each Boston place.", Links.bostonInspections.absoluteString)
                source("Overture Maps Foundation", "Restaurant listings and websites come from Overture Maps Foundation places data (overturemaps.org)\(model.overtureRelease.map { ", release \($0)" } ?? ""), filtered and reformatted for this app.\n• Data from Meta, Microsoft, DAC and BrightQuery. Available under CDLA Permissive 2.0.\n• Data from Foursquare. \(foursquareCopyright) Available under Apache 2.0. Foursquare data was transformed to the Overture schema; this app further filtered and reformatted it. See the NOTICE below.\n• Data from AllThePlaces. Available under CC0 1.0.\nResearched places are put on the map with Overture Maps addresses data (open address sources under permissive licenses, docs.overturemaps.org/attribution).", "https://overturemaps.org")
                source("Honors", "The MICHELIN Guide's selection and James Beard Foundation awards are reported as facts and checked by hand against the official announcements. MICHELIN and the MICHELIN Guide are trademarks of Michelin. James Beard Foundation and James Beard Award are trademarks of the James Beard Foundation. Other names belong to their owners.", "https://guide.michelin.com/us/en/massachusetts/restaurants")
                source("Maps", "Maps, place cards and directions by Apple Maps.", nil)
            }
            Section("Licenses") {
                NavigationLink("Community Data License Agreement – Permissive 2.0") { LicenseText(file: "CDLA-Permissive-2.0", title: "CDLA Permissive 2.0") }
                NavigationLink("Apache License 2.0") { LicenseText(file: "Apache-2.0", title: "Apache License 2.0") }
                NavigationLink("Foursquare OS Places NOTICE") { LicenseText(file: "Foursquare-NOTICE", title: "Foursquare NOTICE") }
            }
            Section("Privacy") {
                Text("The app collects nothing. Your location, if you allow it, only sorts lists by distance and shows where you are on the map, on this device. Saved places stay on this device.")
                    .font(.subheadline).foregroundStyle(Theme.ink2)
                DataUpdatesNote()
                    .font(.footnote).foregroundStyle(Theme.muted)
                Link("Privacy policy", destination: Links.privacy)
                Link("Terms of use", destination: Links.terms)
            }
            Section("Help") {
                Link("Report a missing or closed place", destination: Links.correctionEmail)
                Link("Email \(Links.supportEmail)", destination: URL(string: "mailto:\(Links.supportEmail)")!)
                Link("Website", destination: Links.site)
                Text("Data as of \(DayFormat.text(model.generated) ?? model.generated). Places open and close; check before you go. Version \(Bundle.main.object(forInfoDictionaryKey: "CFBundleShortVersionString") as? String ?? "1.0")")
                    .font(.footnote).foregroundStyle(Theme.muted)
            }
        }
        .navigationTitle("About")
        .tint(Theme.green)
    }

    /// the copyright line exactly as the bundled Foursquare NOTICE has it, so the two can't disagree
    private var foursquareCopyright: String {
        guard let url = Bundle.main.url(forResource: "Foursquare-NOTICE", withExtension: "txt"),
              let text = try? String(contentsOf: url, encoding: .utf8),
              let line = text.split(separator: "\n").first(where: { $0.hasPrefix("©") }) else { return "© Foursquare Labs, Inc. All rights reserved." }
        return line.trimmingCharacters(in: .whitespaces)
    }

    @ViewBuilder
    private func source(_ name: String, _ detail: String, _ url: String?) -> some View {
        VStack(alignment: .leading, spacing: 2) {
            if let url, let u = URL(string: url) { Link(name, destination: u).font(.subheadline.weight(.semibold)) }
            else { Text(name).font(.subheadline.weight(.semibold)) }
            Text(detail).font(.caption).foregroundStyle(Theme.muted)
        }
    }
}

/// A bundled license text (Resources/Licenses), reflowed rather than shown as raw 80-column lines.
struct LicenseText: View {
    let file: String
    let title: String

    var body: some View {
        ScrollView {
            Text(text).font(.footnote).foregroundStyle(Theme.ink).textSelection(.enabled)
                .frame(maxWidth: .infinity, alignment: .leading).padding()
        }
        .inlineTitle(title)
    }

    private var text: String {
        guard let url = Bundle.main.url(forResource: file, withExtension: "txt"),
              let raw = try? String(contentsOf: url, encoding: .utf8) else { return "License text missing." }
        // join hard-wrapped lines into paragraphs; keep blank lines and list items as breaks
        var out: [String] = []
        for para in raw.components(separatedBy: "\n\n") {
            let lines = para.components(separatedBy: "\n").map { $0.trimmingCharacters(in: .whitespaces) }
            var joined = ""
            for l in lines where !l.isEmpty {
                let startsItem = l.hasPrefix("–") || l.hasPrefix("-") || l.range(of: #"^\(?[a-z0-9]{1,3}[.)]\s"#, options: .regularExpression) != nil
                joined += joined.isEmpty ? l : (startsItem ? "\n" + l : " " + l)
            }
            if !joined.isEmpty { out.append(joined) }
        }
        return out.joined(separator: "\n\n")
    }
}
