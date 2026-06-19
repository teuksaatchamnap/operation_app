<template>
    <v-menu v-model="menu" location="bottom end">
        <template v-slot:activator="{ props: menuProps }">
            <v-btn
                variant="text"
                size="small"
                v-bind="menuProps"
            >
                Download <v-icon>mdi-download</v-icon>
            </v-btn>
        </template>
        <v-list density="compact">
            <v-list-item
                prepend-icon="mdi-file-image"
                @click="downloadAs('png')"
            >
                Image (PNG)
            </v-list-item>
            <v-list-item
                prepend-icon="mdi-file-pdf-box"
                @click="downloadAs('pdf')"
            >
                PDF
            </v-list-item>
        </v-list>
    </v-menu>
</template>

<script setup>
import html2canvas from "html2canvas";
import jsPDF from "jspdf";
import { ref } from "vue";

const props = defineProps({
    target: {
        type: [HTMLElement, Object],
        default: null,
    },
    filename: {
        type: String,
        default: "export",
    },
});

const menu = ref(false);

function downloadAs(format) {
    menu.value = false;
    const el = props.target?.$el ?? props.target;
    if (!el) return;

    // Save and restore patches to <style> elements (catches inline/lazy styles)
    const patches = [];
    document.querySelectorAll("style").forEach((s) => {
        if (s.textContent.includes("color(")) {
            patches.push({ el: s, content: s.textContent });
            s.textContent = s.textContent.replace(
                /color\([^)]+\)/g,
                "#000000",
            );
        }
    });

    // Proxy getComputedStyle to intercept color() in computed values
    // (catches external stylesheets like the Tailwind CSS bundle)
    const origGetComputedStyle = window.getComputedStyle.bind(window);
    window.getComputedStyle = function (element, pseudoElt) {
        const style = origGetComputedStyle(element, pseudoElt);
        return new Proxy(style, {
            get(target, prop) {
                const value = target[prop];
                if (typeof value === "function") {
                    return function (...args) {
                        return value.apply(target, args);
                    };
                }
                return typeof value === "string" && value.includes("color(")
                    ? value.replace(/color\([^)]+\)/g, "#000000")
                    : value;
            },
        });
    };

    function cleanup() {
        patches.forEach((p) => (p.el.textContent = p.content));
        window.getComputedStyle = origGetComputedStyle;
    }

    html2canvas(el, {
        scale: 2,
        useCORS: true,
        backgroundColor: "#ffffff",
        onclone: (doc) => {
            // Switch Vuetify theme to light in the cloned document only
            doc.querySelectorAll(".v-theme--dark").forEach((el) => {
                el.classList.remove("v-theme--dark");
                el.classList.add("v-theme--light");
            });
            // Fix ApexCharts SVG text/stroke colors for dark-to-light switch
            const darkText = "#e0e0e0";
            const lightText = "#333333";
            doc.querySelectorAll('[fill="' + darkText + '"]').forEach((el) => {
                el.setAttribute("fill", lightText);
            });
            doc.querySelectorAll('[stroke="' + darkText + '"]').forEach((el) => {
                el.setAttribute("stroke", lightText);
            });
            doc.querySelectorAll('[style*="' + darkText + '"]').forEach((el) => {
                el.style.cssText = el.style.cssText.replace(
                    new RegExp(darkText.replace("#", "\\#"), "g"),
                    lightText,
                );
            });
        },
    })
        .then((canvas) => {
            cleanup();

            const timestamp = new Date().toISOString().slice(0, 10);
            const filename = `${props.filename}-${timestamp}`;

            if (format === "png") {
                canvas.toBlob((blob) => {
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement("a");
                    link.href = url;
                    link.download = `${filename}.png`;
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    URL.revokeObjectURL(url);
                });
            } else {
                canvas.toBlob((blob) => {
                    const reader = new FileReader();
                    reader.onload = () => {
                        const img = new Image();
                        img.onload = () => {
                            const pdf = new jsPDF("p", "mm", "a4");
                            const pdfWidth = pdf.internal.pageSize.getWidth();
                            const pdfHeight =
                                (img.naturalHeight * pdfWidth) /
                                img.naturalWidth;
                            let heightLeft = pdfHeight;
                            let position = 0;
                            const pageHeight =
                                pdf.internal.pageSize.getHeight();

                            pdf.addImage(
                                reader.result,
                                "PNG",
                                0,
                                position,
                                pdfWidth,
                                pdfHeight,
                            );
                            heightLeft -= pageHeight;

                            while (heightLeft > 0) {
                                position = heightLeft - pdfHeight;
                                pdf.addPage();
                                pdf.addImage(
                                    reader.result,
                                    "PNG",
                                    0,
                                    position,
                                    pdfWidth,
                                    pdfHeight,
                                );
                                heightLeft -= pageHeight;
                            }

                            pdf.save(`${filename}.pdf`);
                        };
                        img.src = URL.createObjectURL(blob);
                    };
                    reader.readAsDataURL(blob);
                });
            }
        })
        .catch((err) => {
            cleanup();
            console.error("Export failed:", err);
        });
}
</script>
