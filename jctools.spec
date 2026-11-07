Name:		jctools
Version:	4.0.7
Release:	1
Summary:	Java concurrency queues and counters
Group:		Development/Java
License:	ASL 2.0
URL:		https://github.com/JCTools/JCTools
Source0:	https://github.com/JCTools/JCTools/archive/refs/tags/v%{version}.tar.gz#/jctools-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	python
# Literal, so the first rpmbuild -bs records them before sysjar is installed.
BuildRequires:	maven
BuildRequires:	java-current-devel
BuildSystem:	maven
BuildOption(install):	--file-name jctools-core --link %{name}

Obsoletes:	%{name}-experimental < %{version}-%{release}
Obsoletes:	%{name}-javadoc < %{version}-%{release}
Obsoletes:	%{name}-parent < %{version}-%{release}

%description
JCTools provides lock-free queues and counters that the JDK does not.
4.0.7 is the 4.0.6 code with the JPMS module name fixed to
org.jctools.core. This package builds the core Unsafe and Atomic
queues, including the unpadded variants, for Java 8. The JDK 11
VarHandle artifact, the experimental module, channels, and benchmarks
are not built. Tests are skipped.

%prep
%autosetup -n JCTools-%{version}
python - <<'PY'
import shutil
from pathlib import Path

for name in (
    "jctools-benchmarks",
    "jctools-build",
    "jctools-channels",
    "jctools-concurrency-test",
    "jctools-core-jdk11",
    "jctools-experimental",
):
    shutil.rmtree(name)
core_pom = Path("jctools-core/pom.xml")
if core_pom.exists():
    core_pom.unlink()

stripped = 0
java_files = list(Path("jctools-core/src/main/java").rglob("*.java"))
for path in java_files:
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    new = []
    changed = False
    for line in lines:
        if line.strip() in {"@Export", "import org.osgi.annotation.bundle.Export;"}:
            changed = True
            continue
        new.append(line)
    if changed:
        path.write_text("".join(new), encoding="utf-8")
        stripped += 1
if stripped != 7 or len(java_files) != 114:
    raise SystemExit("stripped " + str(stripped) + " java " + str(len(java_files)))
for path in java_files:
    text = path.read_text(encoding="utf-8")
    if "osgi" in text or "@Export" in text:
        raise SystemExit("osgi remains in " + path.name)

Path("pom.xml").write_text("""<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.jctools</groupId>
  <artifactId>jctools-core</artifactId>
  <version>%{version}</version>
  <packaging>jar</packaging>
  <name>Java Concurrency Tools Core Library</name>
  <description>Lock-free queues and counters from JCTools.</description>
  <url>https://github.com/JCTools/JCTools</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.source>1.8</maven.compiler.source>
    <maven.compiler.target>1.8</maven.compiler.target>
  </properties>
  <build>
    <sourceDirectory>jctools-core/src/main/java</sourceDirectory>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.12.1</version>
        <configuration>
          <source>1.8</source>
          <target>1.8</target>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-jar-plugin</artifactId>
        <version>3.3.0</version>
        <configuration>
          <archive>
            <manifestEntries>
              <Automatic-Module-Name>org.jctools.core</Automatic-Module-Name>
            </manifestEntries>
          </archive>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
""", encoding="utf-8")
pom = Path("pom.xml").read_text(encoding="utf-8")
for needle in (
    "<artifactId>jctools-core</artifactId>",
    "<version>%{version}</version>",
    "<source>1.8</source>",
    "<target>1.8</target>",
    "org.jctools.core",
    "jctools-core/src/main/java",
):
    if needle not in pom:
        raise SystemExit("pom missing " + needle)
for needle in ("SNAPSHOT", "maven-bundle-plugin", "osgi", "<modules>", "<release>"):
    if needle in pom:
        raise SystemExit("pom still contains " + needle)
poms = list(Path(".").rglob("pom.xml"))
if len(poms) != 1:
    raise SystemExit("expected one pom, found " + str(len(poms)))
PY

%build -a
cat > manifest-addition <<'EOF'
Automatic-Module-Name: org.jctools.core
EOF
jar ufm target/jctools-core-%{version}.jar manifest-addition
java --module-path target/jctools-core-%{version}.jar --describe-module org.jctools.core > module-describe.txt
# A versioned jar prints "name@version ... automatic", not "name automatic".
grep -q '^org.jctools.core' module-describe.txt || { cat module-describe.txt; exit 1; }
grep -q ' automatic$' module-describe.txt || { cat module-describe.txt; exit 1; }

%files -f .mfiles
%doc README.md LICENSE
