Name:		java-diff-utils
Version:	4.12
Release:	1
Summary:	Java library for computing and applying diffs
Group:		Development/Java
License:	Apache-2.0
URL:		https://github.com/java-diff-utils/java-diff-utils
# Tag java-diff-utils-parent-4.12. The jgit module is not built.
Source0:	https://github.com/java-diff-utils/java-diff-utils/archive/refs/tags/java-diff-utils-parent-%{version}.tar.gz#/java-diff-utils-%{version}.tar.gz

BuildArch:	noarch
BuildRequires:	java-current-devel
BuildRequires:	sysjar
BuildRequires:	javapackages-filesystem

%description
io.github.java-diff-utils:java-diff-utils %{version} computes diffs and
applies patches. Error Prone 2.50.0 compiles against this version.
The jgit histogram module is not included.

%prep
%autosetup -n java-diff-utils-java-diff-utils-parent-%{version}
find . \( -name '*.jar' -o -name '*.class' -o -name '*.so' -o -name '*.node' -o -name '*.wasm' \) -delete

%build
set -eo pipefail
find java-diff-utils/src/main/java -name '*.java' > sources.list
test "$(wc -l < sources.list)" -eq 30
mkdir -p classes
javac --release 8 -encoding UTF-8 -d classes @sources.list
cat > manifest.mf << 'EOF'
Manifest-Version: 1.0
Automatic-Module-Name: io.github.javadiffutils

EOF
jar cfm java-diff-utils.jar manifest.mf -C classes .
jar i java-diff-utils.jar
javap -verbose -cp java-diff-utils.jar com.github.difflib.DiffUtils | grep -F 'major version: 52'
jar --describe-module --file java-diff-utils.jar > describe.txt
if grep -F -q 'Unable to derive' describe.txt; then
	cat describe.txt
	exit 1
fi
jar tf java-diff-utils.jar | grep -E 'module-info|\.(java|jar|so|node|wasm)$' && exit 1 || true

cat > java-diff-utils.pom << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>io.github.java-diff-utils</groupId>
  <artifactId>java-diff-utils</artifactId>
  <version>4.12</version>
  <name>java-diff-utils</name>
  <description>Java library for computing and applying diffs</description>
  <url>https://github.com/java-diff-utils/java-diff-utils</url>
  <licenses>
    <license>
      <name>Apache License, Version 2.0</name>
      <url>https://www.apache.org/licenses/LICENSE-2.0.txt</url>
    </license>
  </licenses>
</project>
EOF

%install
sysjar install --buildroot %{buildroot} \
	--artifact java-diff-utils.pom:java-diff-utils.jar \
	--file-name java-diff-utils \
	--filelist .mfiles

%check
set -eo pipefail
JAR=%{buildroot}%{_javadir}/java-diff-utils.jar
test -f "$JAR"
mkdir -p check
cat > check/Smoke.java << 'EOF'
import com.github.difflib.DiffUtils;
import com.github.difflib.patch.Patch;
import java.util.Arrays;
import java.util.List;
public class Smoke {
	public static void main(String[] args) throws Exception {
		List<String> original = Arrays.asList("gradle", "a");
		List<String> revised = Arrays.asList("gradle", "b");
		Patch<String> patch = DiffUtils.diff(original, revised);
		List<String> applied = DiffUtils.patch(original, patch);
		System.out.println("jdu_ok " + applied.get(1) + " " + patch.getDeltas().size());
	}
}
EOF
javac --release 8 -encoding UTF-8 -cp "$JAR" -d check check/Smoke.java
java -cp "check:$JAR" Smoke > check/check.log
cat check/check.log
grep -F -q 'jdu_ok b 1' check/check.log

%files -f .mfiles
%license LICENSE
%doc README.md CHANGELOG.md
