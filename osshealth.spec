Name: osshealth
Version: 1.0.0
Release: 0
Summary: osshealth script
License: MIT

Source0: osshealth.py

Requires: python3

%description
osshealth.py script is useful for checking for common errors in Ibmi
environment, that could affect usage of OSS

%install
mkdir -p %{buildroot}/%{_bindir}
install -c %{SOURCE0} %{buildroot}/%{_bindir}

%files
%defattr(-, qsys, *none)
%{_bindir}/osshealth.py

%changelog
* Wed Mar 23 2022 Vasili Skurydzin <vasili.skurydzin@protonmail.com> - 1.0.0
- Initial spec file
