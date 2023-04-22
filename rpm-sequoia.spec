%define		crates_ver	1.4.0

Summary:	An OpenPGP backend for rpm using Sequoia PGP
Name:		rpm-sequoia
Version:	1.4.0
Release:	1
License:	GPL v2+
Group:		Libraries
Source0:	https://github.com/rpm-software-management/rpm-sequoia/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	90e33d96c834e1cf4ac18dcb508d4ecb
Source1:	%{name}-crates-%{crates_ver}.tar.xz
# Source1-md5:	b9628f13f5f4a7d78a5aea61cad6bbec
URL:		https://github.com/rpm-software-management/rpm-sequoia
BuildRequires:	cargo
BuildRequires:	clang
BuildRequires:	gmp-devel
BuildRequires:	nettle-devel
BuildRequires:	rpmbuild(macros) >= 2.011
BuildRequires:	rust >= 1.60.0
BuildRequires:	tar >= 1:1.22
BuildRequires:	xz
ExclusiveArch:	%{rust_arches}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		soname	librpm_sequoia.so.1

%description
This library provides an implementation of the rpm's pgp interface using
Sequoia.

%package devel
Summary:	Development files for rpm-sequoia library
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
Development files for rpm-sequoia library.

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

%cargo_build --frozen

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
%attr(755,root,root) %{_libdir}/librpm_sequoia.so
%{_pkgconfigdir}/rpm-sequoia.pc
