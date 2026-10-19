First cross-project NEXUS software-licence review to inventory dependencies, detect redistribution incompatibilities and define controls for demonstrators, reproducible images and external deliverables.

Clara Ibáñez: We need a common inventory because projects are preparing pilots, demonstrators and reproducible packages.
Sergio Vidal: The initial scan identified 214 direct and 1,486 transitive dependencies across twelve active repositories.
Mireia Soler: Most use permissive licences, but there are nine GPL components and three packages with unidentified licences.
Nuria Castaño: Two container images include commercial tools available only under the institutional licence. They cannot be distributed externally.
Diego Ramos: One entity-linking package contains models whose conditions differ from the code. We must record software and model licences separately.
Andrés Beltrán: ARIADNA and VERDANT need reproducible images. We can publish build recipes and replace restricted components with local installation steps.
Javier Ortega: SILEX will deliver an image to the municipality. We must confirm that its use is covered and that it does not enable unauthorized redistribution.
Sergio Vidal: I propose a manifest for each version containing name, version, source, licence, usage scope and attribution obligation. The pipeline will block dependencies without a recognized licence.
Clara Ibáñez: What do we do with the three unknown packages?
Mireia Soler: One can be replaced. The other two require clarification from the provider before any delivery.
Nuria Castaño: We will also freeze a permitted copy of sources or artifacts so a dependency cannot disappear.
Clara Ibáñez: Approved. No external package will be released without a complete manifest; commercial components remain internal, and unknown licences block delivery.