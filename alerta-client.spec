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
Prefix: /opt
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
%__mkdir_p %{buildroot}/var/lib/alerta

%clean
rm -rf %{buildroot}

%files
%defattr(-,alerta,alerta)
/opt/alerta/client/*
%dir %attr(0775,alerta,root) /var/lib/alerta

%pre
getent group alerta >/dev/null || groupadd -r alerta
getent passwd alerta >/dev/null || \
    useradd -r -g alerta -d /var/lib/alerta -s /sbin/nologin \
    -c "Alerta monitoring tool" alerta
exit 0

%changelog
* Thu Mar 27 2013 Nick Satterly <nick.satterly@theguardian.com> - 3.0.0-2
- Package alerta relase 3.0 command-line tools
