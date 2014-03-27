%define name alerta-client
%define version 3.0.0
%define release 2

Name: %{name}
Summary: Alerta command-line tool
Version: %{version}
Release: %{release}
Source0: %{name}-%{version}.tar.gz
License: MIT
Group: Utilities/System
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: x86_64
Vendor: Nick Satterly <nick.satterly@theguardian.com>
Url: https://github.com/alerta/python-alerta-client
BuildRequires: python-devel, python-setuptools, python-pip, python-virtualenv

%description
Command-line tool for Alerta monitoring framework.

%prep
%setup

%build
/usr/bin/virtualenv --no-site-packages client
client/bin/pip install -r requirements.txt --upgrade
client/bin/python setup.py install --single-version-externally-managed --root=/
/usr/bin/virtualenv --relocatable client

%install
%__mkdir_p %{buildroot}/opt/alerta/client
cp -r %{_builddir}/%{name}-%{version}/client %{buildroot}/opt/alerta

%clean
rm -rf %{buildroot}

%files
/opt/alerta/client/*
%defattr(-,root,root)

%changelog
* Thu Mar 27 2013 Nick Satterly <nick.satterly@theguardian.com> - 3.0.0-2
- Package alerta relase 3.0 command-line tools
