import CoreLocation
import Observation
import UIKit

/// "Near me" sorting. Asks for when-in-use permission only when a list is sorted by distance or "My location" is tapped; the location never leaves the device.
@MainActor
@Observable
final class LocationService: NSObject, CLLocationManagerDelegate {
    private let manager = CLLocationManager()
    private(set) var location: CLLocation?
    private(set) var status: CLAuthorizationStatus = .notDetermined
    /// no fix within 12 seconds, or Core Location reported an error
    private(set) var failed = false
    private var timeout: Task<Void, Never>?
    /// when the current request started: a fix from before it is a cached one (from launch, or before a drive) and doesn't count
    private var askedAt = Date.distantPast

    override init() {
        super.init()
        manager.delegate = self
        manager.desiredAccuracy = kCLLocationAccuracyHundredMeters
        status = manager.authorizationStatus
    }

    var isDenied: Bool { status == .denied || status == .restricted }

    /// Every place is in Massachusetts, so a reader elsewhere (an App Reviewer in California, say) gets told rather than an empty map.
    /// A coarse outline of the state (Idaho's lesson: a bounding box would count Pawtucket, Salem, NH and Nashua),
    /// drawn a little outside the line so the river and bay shores count as inside.
    var isOutsideMassachusetts: Bool {
        guard let c = location?.coordinate else { return false }
        return !MassachusettsOutline.contains(c)
    }

    /// Once location is off for the app, iOS won't ask again; the app's page in Settings is the only way back.
    static func openSettings() {
        if let url = URL(string: UIApplication.openSettingsURLString) { UIApplication.shared.open(url) }
    }

    func request() {
        switch manager.authorizationStatus {
        case .notDetermined: manager.requestWhenInUseAuthorization()
        case .authorizedWhenInUse, .authorizedAlways: locate()
        default: break
        }
    }

    private func locate() {
        failed = false
        let asked = Date()
        askedAt = asked
        manager.requestLocation()
        timeout?.cancel()
        timeout = Task { [weak self] in
            try? await Task.sleep(for: .seconds(12))
            guard let self, !Task.isCancelled else { return }
            if (self.location?.timestamp ?? .distantPast) < asked { self.failed = true }
        }
    }

    nonisolated func locationManagerDidChangeAuthorization(_ m: CLLocationManager) {
        let s = m.authorizationStatus
        Task { @MainActor in
            self.status = s
            if s == .authorizedWhenInUse || s == .authorizedAlways { self.locate() }
        }
    }

    nonisolated func locationManager(_ m: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let l = locations.last else { return }
        Task { @MainActor in
            // "My location" needs a fresh fix on every tap: a cached one from before the request would put you back where you were
            guard l.timestamp >= self.askedAt.addingTimeInterval(-2) else { return }
            self.location = l; self.failed = false; self.timeout?.cancel()
        }
    }

    nonisolated func locationManager(_ m: CLLocationManager, didFailWithError error: Error) {
        Task { @MainActor in if self.location == nil { self.failed = true } }
    }
}

extension CLLocation {
    /// "0.4 mi", "12 mi", "1,012 mi" (an App Reviewer in California is a thousand miles out)
    func milesText(to other: CLLocation) -> String {
        let mi = distance(from: other) / 1609.344
        return (mi < 10 ? mi.formatted(.number.precision(.fractionLength(1))) : Int(mi.rounded()).formatted()) + " mi"
    }
}

/// A coarse Massachusetts outline (longitude, latitude), about 600 m outside the Overture land outline (buffer 0.006°, simplify 0.01°; six
/// rings: the mainland with the Cape, Martha's Vineyard, Nantucket and the Elizabeth Islands). Boston, Williamstown, Attleboro, Methuen,
/// Provincetown, Edgartown, Nantucket and Cuttyhunk are inside; Pawtucket, Salem (NH), Nashua, Enfield (CT), Pownal (VT), Hillsdale (NY)
/// and Block Island are not.
enum MassachusettsOutline {
    static let rings: [[(Double, Double)]] = [
        [(-72.746, 42.03), (-72.764, 41.998), (-72.818, 41.992), (-72.82, 42.031), (-73.502, 42.046), (-73.514, 42.088),
         (-73.268, 42.751), (-71.297, 42.703), (-71.248, 42.748), (-71.188, 42.745), (-71.192, 42.792), (-71.169, 42.814),
         (-71.133, 42.827), (-71.068, 42.813), (-71.034, 42.865), (-70.903, 42.893), (-70.847, 42.867), (-70.809, 42.875),
         (-70.802, 42.796), (-70.765, 42.705), (-70.782, 42.696), (-70.687, 42.658), (-70.628, 42.698), (-70.617, 42.667),
         (-70.582, 42.666), (-70.588, 42.653), (-70.581, 42.627), (-70.626, 42.614), (-70.659, 42.574), (-70.678, 42.581),
         (-70.667, 42.605), (-70.708, 42.567), (-70.861, 42.539), (-70.863, 42.527), (-70.836, 42.521), (-70.841, 42.505),
         (-70.826, 42.506), (-70.831, 42.487), (-70.89, 42.456), (-70.929, 42.455), (-70.904, 42.411), (-70.94, 42.412),
         (-70.949, 42.45), (-70.956, 42.445), (-70.983, 42.408), (-70.961, 42.391), (-70.948, 42.341), (-70.981, 42.359),
         (-71.037, 42.306), (-70.98, 42.333), (-70.982, 42.315), (-70.994, 42.32), (-70.999, 42.312), (-70.983, 42.301),
         (-71.012, 42.287), (-70.985, 42.27), (-70.935, 42.308), (-70.882, 42.316), (-70.85, 42.275), (-70.779, 42.25),
         (-70.763, 42.258), (-70.744, 42.226), (-70.712, 42.21), (-70.714, 42.164), (-70.637, 42.095), (-70.638, 42.054),
         (-70.593, 42.005), (-70.641, 41.99), (-70.64, 42.017), (-70.62, 42.013), (-70.648, 42.042), (-70.666, 42.041),
         (-70.665, 42.005), (-70.691, 42.012), (-70.705, 42.006), (-70.649, 41.956), (-70.653, 41.985), (-70.619, 41.949),
         (-70.583, 41.956), (-70.535, 41.931), (-70.52, 41.858), (-70.536, 41.82), (-70.472, 41.768), (-70.405, 41.749),
         (-70.286, 41.74), (-70.257, 41.72), (-70.191, 41.758), (-70.028, 41.789), (-70.008, 41.812), (-70.01, 41.887),
         (-70.04, 41.922), (-70.076, 41.893), (-70.097, 42.024), (-70.159, 42.055), (-70.19, 42.033), (-70.163, 42.031),
         (-70.192, 42.014), (-70.251, 42.067), (-70.197, 42.089), (-70.113, 42.073), (-70.05, 42.041), (-69.971, 41.931),
         (-69.934, 41.828), (-69.931, 41.667), (-69.962, 41.636), (-69.985, 41.547), (-70.009, 41.534), (-70.014, 41.56),
         (-69.976, 41.649), (-70.015, 41.666), (-70.176, 41.645), (-70.266, 41.603), (-70.274, 41.626), (-70.348, 41.629),
         (-70.38, 41.605), (-70.432, 41.603), (-70.485, 41.548), (-70.623, 41.535), (-70.653, 41.51), (-70.67, 41.517),
         (-70.754, 41.473), (-70.788, 41.441), (-70.838, 41.437), (-70.844, 41.459), (-70.81, 41.459), (-70.667, 41.546),
         (-70.648, 41.579), (-70.659, 41.641), (-70.639, 41.655), (-70.667, 41.684), (-70.631, 41.709), (-70.644, 41.714),
         (-70.676, 41.686), (-70.664, 41.713), (-70.712, 41.735), (-70.712, 41.672), (-70.756, 41.706), (-70.738, 41.675),
         (-70.757, 41.67), (-70.761, 41.637), (-70.801, 41.646), (-70.802, 41.621), (-70.852, 41.624), (-70.844, 41.606),
         (-70.817, 41.604), (-70.819, 41.578), (-70.84, 41.588), (-70.857, 41.577), (-70.886, 41.626), (-70.905, 41.616),
         (-70.897, 41.587), (-70.924, 41.608), (-70.928, 41.578), (-70.941, 41.578), (-70.922, 41.538), (-70.943, 41.532),
         (-70.951, 41.509), (-70.974, 41.525), (-70.978, 41.505), (-71.017, 41.503), (-71.037, 41.476), (-71.051, 41.497),
         (-71.083, 41.504), (-71.123, 41.493), (-71.148, 41.612), (-71.139, 41.655), (-71.199, 41.67), (-71.177, 41.703),
         (-71.228, 41.706), (-71.265, 41.747), (-71.346, 41.795), (-71.346, 41.892), (-71.387, 41.892), (-71.387, 42.013),
         (-71.799, 42.002), (-71.806, 42.018), (-72.607, 42.019), (-72.7, 42.031)],
        [(-70.241, 41.29), (-70.068, 41.313), (-70.031, 41.367), (-70.05, 41.398), (-70.014, 41.368), (-69.956, 41.263),
         (-69.97, 41.243), (-70.01, 41.233), (-70.114, 41.236), (-70.25, 41.283), (-70.284, 41.315), (-70.246, 41.312)],
        [(-70.772, 41.359), (-70.704, 41.439), (-70.604, 41.489), (-70.591, 41.466), (-70.559, 41.474), (-70.542, 41.42),
         (-70.496, 41.392), (-70.453, 41.427), (-70.44, 41.4), (-70.454, 41.344), (-70.707, 41.337), (-70.744, 41.326),
         (-70.775, 41.295), (-70.844, 41.346), (-70.812, 41.363)],
        [(-70.825, 41.246), (-70.835, 41.264), (-70.797, 41.261), (-70.801, 41.245)],
        [(-70.915, 41.43), (-70.857, 41.456), (-70.842, 41.433), (-70.864, 41.417), (-70.956, 41.41), (-70.93, 41.437)],
        [(-70.942, 42.32), (-70.932, 42.339), (-70.918, 42.328), (-70.928, 42.313)]]

    static func contains(_ c: CLLocationCoordinate2D) -> Bool { rings.contains { contains(c, ring: $0) } }

    /// Ray casting: a point is inside when a ray east of it crosses the outline an odd number of times.
    static func contains(_ c: CLLocationCoordinate2D, ring: [(Double, Double)]) -> Bool {
        var inside = false
        var j = ring.count - 1
        for i in 0..<ring.count {
            let (xi, yi) = ring[i], (xj, yj) = ring[j]
            if (yi > c.latitude) != (yj > c.latitude) && c.longitude < (xj - xi) * (c.latitude - yi) / (yj - yi) + xi { inside.toggle() }
            j = i
        }
        return inside
    }
}
