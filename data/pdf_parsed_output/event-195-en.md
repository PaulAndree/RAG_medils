Second software-licence review to resolve pending components, verify autumn-version manifests and authorize or block planned deliverables.

Clara Ibáñez: In July, three packages had unknown licences, and two images contained internal commercial components.
Sergio Vidal: One unknown package was replaced. The provider clarified that another uses Apache-2.0. The third provider did not respond, and the package was removed from all delivery branches.
Mireia Soler: The nine GPL components are correctly isolated. They are not linked incompatibly with modules distributed under permissive licences.
Nuria Castaño: The two images containing commercial tools remain internal. For external deliveries, we generated build recipes that request local installation where a licence exists.
Javier Ortega: The SILEX image intended for the municipality has a complete manifest and contains no commercial components.
Lucía Navarro: LUMEN demo-1.0 will list code, model and reproduction licences separately. Image rights will not be confused with the software licence.
Andrés Beltrán: ARIADNA v2.2 will release code and configuration, but not the closed test set or access-restricted artifacts.
Diego Ramos: Entity-linking models now have their own cards containing source, version and usage conditions.
Sergio Vidal: The pipeline blocked two builds because of new dependencies without manifests and released them after the information was completed.
Clara Ibáñez: Which deliveries are authorized?
Sergio Vidal: SILEX 1.0, LUMEN demo-1.0, ARIADNA v2.2 and VERDANT recipes are authorized. Internal images remain non-redistributable.
Clara Ibáñez: Approved. The licence manifest becomes mandatory evidence for every delivery and final archive.