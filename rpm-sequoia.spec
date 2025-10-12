%define		crates_ver	1.9.0

Summary:	An OpenPGP backend for rpm using Sequoia PGP
Summary(pl.UTF-8):	Backend OpenPGP dla rpm-a wykorzystujący Sequoia PGP
Name:		rpm-sequoia
Version:	1.9.0
Release:	1
License:	GPL v2+
Group:		Libraries
Source0:	https://github.com/rpm-software-management/rpm-sequoia/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	f3fdda80dad5b6907775c64fec988c04
Source1:	%{name}-crates-%{crates_ver}.tar.xz
# Source1-md5:	9f60280809bdeb74d71740449b469f16
URL:		https://github.com/rpm-software-management/rpm-sequoia
BuildRequires:	cargo
BuildRequires:	openssl-devel
BuildRequires:	rpmbuild(macros) >= 2.050
BuildRequires:	rust >= 1.85.0
BuildRequires:	sed >= 4.0
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
%{?rust_req}
Requires:	crypto-policies
ExclusiveArch:	%{rust_arches}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		soname	librpm_sequoia.so.1

%description
This library provides an implementation of the rpm's pgp interface
using Sequoia.

%description -l pl.UTF-8
Ta biblioteka zawiera implementację interfejsu pgp rpm-a
wykorzystującą Sequoia.

%package devel
Summary:	Development files for rpm-sequoia library
Summary(pl.UTF-8):	Pliki programistyczne biblioteki rpm-sequoia
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Development files for rpm-sequoia library.

%description devel -l pl.UTF-8
Pliki programistyczne biblioteki rpm-sequoia.

%prep
%setup -q -a1

%{__mv} %{name}-%{crates_ver}/* .
sed -i -e 's/@@VERSION@@/%{version}/' Cargo.lock

# use our offline registry
export CARGO_HOME="$(pwd)/.cargo"

mkdir -p "$CARGO_HOME"
cat >>.cargo/config.toml <<EOF
[source.crates-io]
registry = 'https://github.com/rust-lang/crates.io-index'
replace-with = 'vendored-sources'

[source.vendored-sources]
directory = '$PWD/vendor'
EOF

%build
export CARGO_HOME="$(pwd)/.cargo"
export PREFIX="%{_prefix}"
export LIBDIR="%{_libdir}"

%cargo_build --frozen --no-default-features -F crypto-openssl

%install
rm -rf $RPM_BUILD_ROOT

objdump -p %{cargo_objdir}/librpm_sequoia.so | grep -q 'SONAME[[:space:]]*%{soname}$'

install -D %{cargo_objdir}/librpm_sequoia.so $RPM_BUILD_ROOT/%{_libdir}/%{soname}
ln -s %{soname} $RPM_BUILD_ROOT/%{_libdir}/librpm_sequoia.so
install -D %{cargo_targetdir}/%{!?debug:release}%{?debug:debug}/rpm-sequoia.pc $RPM_BUILD_ROOT%{_pkgconfigdir}/rpm-sequoia.pc

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README.md
%attr(755,root,root) %{_libdir}/%{soname}

%files devel
%defattr(644,root,root,755)
%{_libdir}/librpm_sequoia.so
%{_pkgconfigdir}/rpm-sequoia.pc
