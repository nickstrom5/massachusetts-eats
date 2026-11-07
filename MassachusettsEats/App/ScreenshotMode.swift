import Foundation
import CoreLocation
import UIKit

/// `-screenshot <name>` opens one screen with fixed state for App Store screenshots (scripts/capture-screenshots.sh).
/// Names: home, beef, clams, northend, portuguese, diners, chinatown, taverns, honors, oldest, detail, map, saved, about.
enum ScreenshotMode {
    /// Debug builds only: an App Store build ignores the launch argument, so no one can reach seeded screens or fake locations.
    static var name: String? {
        #if DEBUG
        let args = ProcessInfo.processInfo.arguments
        guard let i = args.firstIndex(of: "-screenshot"), i + 1 < args.count else { return nil }
        return args[i + 1]
        #else
        return nil
        #endif
    }
    static var isActive: Bool { name != nil }

    @MainActor
    static func apply(to model: AppModel) {
        guard let name, model.isLoaded else { return }
        model.filters = Filters()
        // Boston's Faneuil Hall, so "nearest" lists have distances without a permission prompt
        model.screenshotLocation = CLLocation(latitude: 42.3600, longitude: -71.0547)
        // by name and town, ignoring case, so a rebuild with a slightly different casing still finds the place; the hand-checked one first
        let pick = { (n: String, town: String?) -> Place? in
            let hits = model.places.filter { $0.name.caseInsensitiveCompare(n) == .orderedSame && (town == nil || $0.city == town) }
            return hits.first(where: \.handChecked) ?? hits.first
        }
        for p in [pick("Union Oyster House", "Boston"), pick("Woodman's of Essex", "Essex"), pick("Kelly's Roast Beef", "Revere")]
            .compactMap({ $0 }) where !model.isSaved(p) {
            model.toggleSaved(p)
        }
        let open = { (g: Guide) in model.tab = .guides; model.selectedGuide = g; model.guidesPath = [.guide(g)] }
        switch name {
        case "beef":
            // Salem, among the North Shore roast beef shops
            model.screenshotLocation = CLLocation(latitude: 42.5195, longitude: -70.8967)
            open(.beef)
        case "clams": open(.clams)
        case "northend": open(.northEnd)
        case "portuguese":
            // Fall River's Columbia Street
            model.screenshotLocation = CLLocation(latitude: 41.6945, longitude: -71.1600)
            open(.portuguese)
        case "diners":
            // Worcester's Kelley Square, near the lunch-car diners
            model.screenshotLocation = CLLocation(latitude: 42.2560, longitude: -71.7990)
            open(.diners)
        case "chinatown": open(.chinatown)
        case "taverns": open(.taverns)
        case "honors": open(.honors)
        case "oldest": open(.oldest)
        case "detail":
            // Union Oyster House: a historic tavern with its 1826 founding year and its note
            open(.taverns)
            if let p = pick("Union Oyster House", "Boston") ?? model.places.first {
                model.selectedPlace = p; model.guidesPath.append(.place(p))
            }
        case "map": model.tab = .map
        case "saved": model.tab = .saved
        case "about": model.tab = .about
        default: model.tab = .guides; model.selectedGuide = nil
        }
        // iPad shows the place column next to every list, so give each shot a place instead of "Pick a place": a different
        // honored or hand-checked one per shot.
        guard UIDevice.current.userInterfaceIdiom == .pad, model.selectedPlace == nil else { return }
        let place: Place? = switch name {
        case "home": pick("Union Oyster House", "Boston")
        case "beef": pick("Kelly's Roast Beef", "Revere")
        case "clams": pick("Woodman's of Essex", "Essex")
        case "northend": pick("Cantina Italiana", "Boston")
        case "portuguese": pick("Sagres Restaurant", "Fall River")
        case "diners": pick("Miss Worcester Diner", "Worcester")
        case "chinatown": pick("China Pearl Restaurant", "Boston")
        case "taverns": pick("Longfellow's Wayside Inn", "Sudbury")
        case "map": pick("Union Oyster House", "Boston")
        case "honors": pick("311 Omakase", "Boston")
        case "oldest": pick("Longfellow's Wayside Inn", "Sudbury")
        case "saved": pick("Woodman's of Essex", "Essex")
        case "about": nil
        default: pick("Union Oyster House", "Boston")
        }
        model.selectedPlace = place
    }
}
