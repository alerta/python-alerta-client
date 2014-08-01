%define name alerta
%define version 3.2.1
%define release 2

Name: %{name}
Summary: Alerta unified command-line tool
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
License: MIT
Group: Utilities/System
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: noarch
Vendor: Nick Satterly <nick.satterly@theguardian.com>
Url: https://github.com/alerta/python-alerta-client
Requires: python-argparse, python-requests, pytz

%description
Unified command-line tool for Alerta monitoring system

%prep
%setup

%build
python setup.py build

%install
python setup.py install --single-version-externally-managed --root=%{buildroot} --record=INSTALLED_FILES

%__mkdir_p %{buildroot}%{_sysconfdir}/profile.d/
echo -e "export ALERTA_ENDPOINT=http://monitoring.guprod.gnm:8080" >%{buildroot}%{_sysconfdir}/profile.d/%{name}.sh

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_bindir}/alerta
%{python_sitelib}/*
%config(noreplace) %{_sysconfdir}/profile.d/%{name}.sh

%changelog
* Fri Aug 01 2014 Nick Satterly <nick.satterly@theguardian.com> - 3.2.1-2
- Use /etc/profile.d for endpoint env var configuration
* Fri Aug 01 2014 Nick Satterly <nick.satterly@theguardian.com> - 3.2.1-1
- Bugfix: problem reading DEFAULT options from config file
* Fri Aug 01 2014 Nick Satterly <nick.satterly@theguardian.com> - 3.2.0-1
- Release 3.2
* Tue Mar 25 2014 Nick Satterly <nick.satterly@theguardian.com> - 3.0.0-1
- Release 3
