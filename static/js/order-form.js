
/* Getting address information from zipcode */
function getAddress() {
    var postalCode = document.getElementById("id_postal_code");

    if (/^([0-9]{5}-[0-9]{3})$/.test(postalCode.value)) {
        var address = document.getElementById("id_address")
        var state = document.getElementById("id_state")
        var city = document.getElementById("id_city")
        var district = document.getElementById("id_district")

        fetch(`https://viacep.com.br/ws/${postalCode.value}/json/`)

            .then(response => response.json())
            .then(data => {
                address.value = "logradouro" in data ? data.logradouro : ""
                state.value = "uf" in data ? data.uf : ""
                city.value = "localidade" in data ? data.localidade : ""
                district.value = "bairro" in data ? data.bairro : ""
            })
            .catch(() => {
                address.value = state.value = city.value = district.value = ""

            })
    }
}