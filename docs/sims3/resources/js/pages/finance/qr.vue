<template>
<div>

    <h2>ABA KHQR Payment</h2>

    <button @click="generateQR">
        Generate QR
    </button>

    <div v-if="qrImage" style="margin-top:20px">
        <img :src="qrImage" width="300">
    </div>

</div>
</template>

<script>

export default {

    data(){
        return{
            qrImage:null
        }
    },
    mounted(){
        this.generateQR()
    },
    methods:{
        generateQR(){
            axios.get('/api/payway/qr')
            .then(response => {
                this.qrImage = response.data.qrImage

            })

        }

    }

}

</script>