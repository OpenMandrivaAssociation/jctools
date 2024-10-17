%{?_javapackages_macros:%_javapackages_macros}

%global namedreltag %nil
%global namedversion %{version}%{?namedreltag}

Name:          jctools
Version:       2.0.2
Release:       2.1
Summary:       Java Concurrency Tools for the JVM
Group:         Development/Java
License:       ASL 2.0
URL:           https://jctools.github.io/JCTools/
Source0:       https://github.com/JCTools/JCTools/archive/v%{namedversion}/%{name}-%{namedversion}.tar.gz

BuildRequires: maven-local
BuildRequires: mvn(junit:junit)
BuildRequires: mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires: mvn(org.hamcrest:hamcrest-all)
BuildRequires: mvn(org.ow2.asm:asm-all)

BuildArch:     noarch

%description
This project aims to offer some concurrent data structures
currently missing from the JDK:

° SPSC/MPSC/SPMC/MPMC Bounded lock free queues
° SPSC/MPSC Unbounded lock free queues
° Alternative interfaces for queues
° Offheap concurrent ring buffer for ITC/IPC purposes
° Single Writer Map/Set implementations
° Low contention stats counters
° Executor

%package experimental
Summary:       JCTools Experimental implementations

%description experimental
Experimental implementations for the
Java Concurrency Tools Library.

%package javadoc
Summary:       Javadoc for %{name}

%description javadoc
This package contains javadoc for %{name}.

%package parent
Summary:       JCTools Parent POM

%description parent
JCTools Parent POM.

%prep
%setup -q -n JCTools-%{namedversion}
# Cleanup
find . -name '*.class' -print -delete
find . -name '*.jar' -print -delete

%pom_xpath_set pom:project/pom:version %{namedversion}
%pom_xpath_set -r pom:parent/pom:version %{namedversion} %{name}-core %{name}-experimental

# Prevent build failure
%pom_remove_plugin :maven-enforcer-plugin

# Unavailable deps
%pom_disable_module %{name}-benchmarks
%pom_disable_module %{name}-concurrency-test

# This dep is unused and unneeded
%pom_remove_dep "com.google.guava:guava-testlib" jctools-experimental

# Not available
%pom_remove_plugin :cobertura-maven-plugin %{name}-core

# Useless tasks
%pom_remove_plugin :maven-source-plugin %{name}-core
%pom_xpath_remove "pom:plugin[pom:artifactId = 'maven-javadoc-plugin']/pom:executions" %{name}-core

# Add OSGi support
for mod in core experimental; do
 %pom_xpath_set "pom:project/pom:packaging" bundle %{name}-${mod}
 %pom_add_plugin org.apache.felix:maven-bundle-plugin:2.3.7 %{name}-${mod} '
 <extensions>true</extensions>
 <executions>
   <execution>
     <id>bundle-manifest</id>
     <phase>process-classes</phase>
     <goals>
       <goal>manifest</goal>
     </goals>
   </execution>
 </executions>
 <configuration>
  <excludeDependencies>true</excludeDependencies>
 </configuration>'
done

%build

%mvn_build -s

%install
%mvn_install

%files -f .mfiles-%{name}-core
%doc README.md
%doc LICENSE

%files experimental -f .mfiles-%{name}-experimental

%files javadoc -f .mfiles-javadoc
%doc LICENSE

%files parent -f .mfiles-%{name}-parent
%doc LICENSE

%changelog
* Sun Sep 17 2017 Mat Booth <mat.booth@redhat.com> - 2.0.2-2
- Drop unneeded dep on guava-testlib

* Mon Aug 14 2017 Tomas Repik <trepik@redhat.com> - 2.0.2-1
- Update to 2.0.2

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Sep 28 2016 gil cattaneo <puntogil@libero.it> 1.2.1-1
- update to 1.2.1

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 1.1-0.3.alpha
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.1-0.2.alpha
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Tue May 19 2015 gil cattaneo <puntogil@libero.it> 1.1-0.1.alpha
- initial rpm

